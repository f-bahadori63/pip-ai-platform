[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [string]$Region = "us-central1",
    [string]$SqlInstance = "pip-mvp-postgres",
    [string]$DatabaseName = "pip_db",
    [string]$CloudDatabaseUser = "pip_user",
    [string]$LocalContainer = "pip-postgres",
    [string]$LocalDatabaseUser = "pip_user",
    [string]$LocalDatabaseName = "pip_db",
    [string]$BucketName = "",
    [string]$DumpPath = ".\pip-mvp-data.sql"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Assert-LastExitCode([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    throw "Google Cloud CLI (gcloud) is not installed or is not on PATH."
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or is not on PATH."
}

if (-not $BucketName) {
    $BucketName = "$ProjectId-pip-mvp-import"
}

$running = & docker inspect `
    --format="{{.State.Running}}" `
    $LocalContainer 2>$null

if ($LASTEXITCODE -ne 0 -or $running -ne "true") {
    throw "Local PostgreSQL container '$LocalContainer' is not running."
}

$confirmation = Read-Host `
    "This replaces schema/data in Cloud SQL database '$DatabaseName'. Type MIGRATE to continue"

if ($confirmation -ne "MIGRATE") {
    Write-Host "Migration cancelled."
    exit 0
}

$fullDumpPath = [IO.Path]::GetFullPath($DumpPath)
Write-Host "Creating a byte-safe PostgreSQL dump at $fullDumpPath..." -ForegroundColor Cyan

$startInfo = New-Object Diagnostics.ProcessStartInfo
$startInfo.FileName = "docker"
$startInfo.Arguments = (
    "exec $LocalContainer pg_dump " +
    "-U $LocalDatabaseUser " +
    "-d $LocalDatabaseName " +
    "--clean --if-exists --no-owner --no-acl --format=plain"
)
$startInfo.UseShellExecute = $false
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.CreateNoWindow = $true

$process = New-Object Diagnostics.Process
$process.StartInfo = $startInfo
[void]$process.Start()

$outputFile = [IO.File]::Create($fullDumpPath)

try {
    $process.StandardOutput.BaseStream.CopyTo($outputFile)
}
finally {
    $outputFile.Dispose()
}

$dumpError = $process.StandardError.ReadToEnd()
$process.WaitForExit()

if ($process.ExitCode -ne 0) {
    throw "pg_dump failed: $dumpError"
}

if ((Get-Item $fullDumpPath).Length -eq 0) {
    throw "The generated database dump is empty."
}

& gcloud config set project $ProjectId
Assert-LastExitCode "Selecting the Google Cloud project"

$bucketUri = "gs://$BucketName"
& gcloud storage buckets describe $bucketUri `
    --project $ProjectId 2>$null | Out-Null

if ($LASTEXITCODE -ne 0) {
    & gcloud storage buckets create $bucketUri `
        --project $ProjectId `
        --location $Region `
        --uniform-bucket-level-access
    Assert-LastExitCode "Creating the migration bucket"
}

$instanceServiceAccount = & gcloud sql instances describe $SqlInstance `
    --project $ProjectId `
    --format="value(serviceAccountEmailAddress)"
Assert-LastExitCode "Reading the Cloud SQL service account"

& gcloud storage buckets add-iam-policy-binding $bucketUri `
    --member "serviceAccount:$instanceServiceAccount" `
    --role "roles/storage.objectAdmin" `
    --condition=None | Out-Null
Assert-LastExitCode "Granting Cloud SQL access to the migration bucket"

$objectName = "pip-mvp-data-$([DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')).sql"
$objectUri = "$bucketUri/$objectName"

$uploaded = $false

try {
    Write-Host "Uploading database dump..." -ForegroundColor Cyan
    & gcloud storage cp $fullDumpPath $objectUri --project $ProjectId
    Assert-LastExitCode "Uploading the database dump"
    $uploaded = $true

    Write-Host "Importing data into Cloud SQL..." -ForegroundColor Cyan
    & gcloud sql import sql $SqlInstance $objectUri `
        --project $ProjectId `
        --database $DatabaseName `
        --user $CloudDatabaseUser `
        --quiet
    Assert-LastExitCode "Importing the PostgreSQL dump"
}
finally {
    # The dump contains project data. Remove the cloud copy even when the
    # import fails; the byte-safe local dump remains available for a retry.
    if ($uploaded) {
        & gcloud storage rm $objectUri --project $ProjectId

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Could not remove temporary cloud object $objectUri"
        }
    }
}

Write-Host ""
Write-Host "Database migration completed successfully." -ForegroundColor Green
Write-Host "Local backup retained at: $fullDumpPath"
Write-Host "Delete that file after verifying the Cloud Run application." -ForegroundColor Yellow
