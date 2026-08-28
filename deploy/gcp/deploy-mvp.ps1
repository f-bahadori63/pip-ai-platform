[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [string]$Region = "us-central1",
    [string]$ServiceName = "pip-mvp",
    [string]$SqlInstance = "pip-mvp-postgres",
    [string]$DatabaseName = "pip_db",
    [string]$DatabaseUser = "pip_user",
    [string]$RuntimeServiceAccount = "pip-mvp-runtime",
    [string]$DatabasePasswordSecret = "pip-mvp-db-password"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Assert-LastExitCode([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

function ConvertTo-PlainText([System.Security.SecureString]$SecureValue) {
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)

    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    throw "Google Cloud CLI (gcloud) is not installed or is not on PATH."
}

Write-Host "Configuring Google Cloud project $ProjectId..." -ForegroundColor Cyan
& gcloud config set project $ProjectId
Assert-LastExitCode "Selecting the Google Cloud project"

$services = @(
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com"
)

& gcloud services enable $services --project $ProjectId
Assert-LastExitCode "Enabling Google Cloud APIs"

& gcloud sql instances describe $SqlInstance `
    --project $ProjectId `
    --format="value(name)" 2>$null | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating Cloud SQL PostgreSQL instance..." -ForegroundColor Cyan
    & gcloud sql instances create $SqlInstance `
        --project $ProjectId `
        --region $Region `
        --database-version POSTGRES_16 `
        --edition ENTERPRISE `
        --tier db-f1-micro `
        --availability-type zonal `
        --storage-type SSD `
        --storage-size 10 `
        --storage-auto-increase `
        --backup-start-time 03:00 `
        --retained-backups-count 7
    Assert-LastExitCode "Creating the Cloud SQL instance"
}
else {
    Write-Host "Cloud SQL instance already exists." -ForegroundColor Green
}

& gcloud sql databases describe $DatabaseName `
    --instance $SqlInstance `
    --project $ProjectId `
    --format="value(name)" 2>$null | Out-Null

if ($LASTEXITCODE -ne 0) {
    & gcloud sql databases create $DatabaseName `
        --instance $SqlInstance `
        --project $ProjectId
    Assert-LastExitCode "Creating the application database"
}

$securePassword = Read-Host `
    "Enter a password for Cloud SQL user '$DatabaseUser'" `
    -AsSecureString
$dbPassword = ConvertTo-PlainText $securePassword

if ([string]::IsNullOrWhiteSpace($dbPassword)) {
    $securePassword.Dispose()
    $dbPassword = $null
    throw "The database password cannot be empty."
}

try {
    $existingUser = & gcloud sql users list `
        --instance $SqlInstance `
        --project $ProjectId `
        --filter="name=$DatabaseUser" `
        --format="value(name)"
    Assert-LastExitCode "Reading Cloud SQL users"

    if ($existingUser) {
        & gcloud sql users set-password $DatabaseUser `
            --instance $SqlInstance `
            --project $ProjectId `
            --password $dbPassword
        Assert-LastExitCode "Updating the Cloud SQL user password"
    }
    else {
        & gcloud sql users create $DatabaseUser `
            --instance $SqlInstance `
            --project $ProjectId `
            --password $dbPassword
        Assert-LastExitCode "Creating the Cloud SQL user"
    }

    & gcloud secrets describe $DatabasePasswordSecret `
        --project $ProjectId `
        --format="value(name)" 2>$null | Out-Null

    if ($LASTEXITCODE -ne 0) {
        & gcloud secrets create $DatabasePasswordSecret `
            --project $ProjectId `
            --replication-policy automatic
        Assert-LastExitCode "Creating the database password secret"
    }

    $secretFile = [IO.Path]::GetTempFileName()

    try {
        $utf8NoBom = New-Object Text.UTF8Encoding($false)
        [IO.File]::WriteAllText($secretFile, $dbPassword, $utf8NoBom)

        & gcloud secrets versions add $DatabasePasswordSecret `
            --project $ProjectId `
            --data-file $secretFile
        Assert-LastExitCode "Adding the database password secret version"
    }
    finally {
        Remove-Item $secretFile -Force -ErrorAction SilentlyContinue
    }
}
finally {
    $dbPassword = $null
    $securePassword.Dispose()
}

$projectNumber = & gcloud projects describe $ProjectId `
    --format="value(projectNumber)"
Assert-LastExitCode "Reading the Google Cloud project number"

# Source deployments use the Compute Engine default service account for Cloud
# Build unless the project overrides it. Google requires run.builder for this
# workflow.
$buildServiceAccount = "$projectNumber-compute@developer.gserviceaccount.com"
& gcloud projects add-iam-policy-binding $ProjectId `
    --member "serviceAccount:$buildServiceAccount" `
    --role "roles/run.builder" `
    --condition=None | Out-Null
Assert-LastExitCode "Granting the Cloud Run Builder role"

$runtimeEmail = "$RuntimeServiceAccount@$ProjectId.iam.gserviceaccount.com"

& gcloud iam service-accounts describe $runtimeEmail `
    --project $ProjectId `
    --format="value(email)" 2>$null | Out-Null

if ($LASTEXITCODE -ne 0) {
    & gcloud iam service-accounts create $RuntimeServiceAccount `
        --project $ProjectId `
        --display-name "PIP MVP Cloud Run runtime"
    Assert-LastExitCode "Creating the runtime service account"
}

& gcloud projects add-iam-policy-binding $ProjectId `
    --member "serviceAccount:$runtimeEmail" `
    --role "roles/cloudsql.client" `
    --condition=None | Out-Null
Assert-LastExitCode "Granting Cloud SQL access"

& gcloud secrets add-iam-policy-binding $DatabasePasswordSecret `
    --project $ProjectId `
    --member "serviceAccount:$runtimeEmail" `
    --role "roles/secretmanager.secretAccessor" `
    --condition=None | Out-Null
Assert-LastExitCode "Granting Secret Manager access"

$connectionName = & gcloud sql instances describe $SqlInstance `
    --project $ProjectId `
    --format="value(connectionName)"
Assert-LastExitCode "Reading the Cloud SQL connection name"

$environmentVariables = @(
    "CLOUD_SQL_CONNECTION_NAME=$connectionName",
    "DB_USER=$DatabaseUser",
    "DB_NAME=$DatabaseName",
    "AI_ENABLED=false",
    "SQL_ECHO=false"
) -join ","

Write-Host "Building and deploying the single-container MVP..." -ForegroundColor Cyan
& gcloud run deploy $ServiceName `
    --project $ProjectId `
    --region $Region `
    --source . `
    --service-account $runtimeEmail `
    --set-cloudsql-instances $connectionName `
    --set-env-vars $environmentVariables `
    --set-secrets "DB_PASS=$DatabasePasswordSecret`:latest" `
    --port 8080 `
    --cpu 1 `
    --memory 1Gi `
    --concurrency 40 `
    --min-instances 0 `
    --max-instances 2 `
    --allow-unauthenticated `
    --quiet
Assert-LastExitCode "Deploying the Cloud Run service"

$serviceUrl = & gcloud run services describe $ServiceName `
    --project $ProjectId `
    --region $Region `
    --format="value(status.url)"
Assert-LastExitCode "Reading the Cloud Run service URL"

Write-Host ""
Write-Host "PIP MVP deployed successfully." -ForegroundColor Green
Write-Host "Application: $serviceUrl"
Write-Host "Health check: $serviceUrl/api/health"
Write-Host ""
Write-Host "Next: run migrate-postgres-data.ps1 to copy the current local data." -ForegroundColor Yellow
