param(
    [string]$ProjectRoot = (Get-Location).Path
)

$ErrorActionPreference = "Continue"

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ExportRoot = Join-Path $ProjectRoot "_gemini_export_$Timestamp"

$Dirs = @(
    "00_MASTER",
    "01_PROJECT",
    "02_BACKEND",
    "03_FRONTEND",
    "04_AI_RAG",
    "05_RUNTIME",
    "06_DOCKER",
    "07_REPORTS",
    "08_GIT",
    "09_SECURITY"
)

foreach ($Dir in $Dirs) {
    New-Item -ItemType Directory -Path (Join-Path $ExportRoot $Dir) -Force | Out-Null
}

function Write-TextFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $Parent = Split-Path $Path -Parent

    if (!(Test-Path $Parent)) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }

    Set-Content -Path $Path -Value $Content -Encoding UTF8
}

function Invoke-NativeSafe {
    param(
        [string]$Command,
        [string[]]$Arguments = @()
    )

    try {
        if (!(Get-Command $Command -ErrorAction SilentlyContinue)) {
            return "COMMAND_NOT_FOUND: $Command"
        }

        $Output = & $Command @Arguments 2>&1

        if ($null -eq $Output) {
            return ""
        }

        return ($Output | Out-String -Width 500)
    }
    catch {
        return "COMMAND_ERROR: $Command`n$($_.Exception.Message)"
    }
}

function Redact-Secrets {
    param(
        [string]$Text
    )

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $Text
    }

    $Patterns = @(
        '(?im)(POSTGRES_PASSWORD\s*[:=]\s*)([^\r\n]+)',
        '(?im)(PGADMIN_DEFAULT_PASSWORD\s*[:=]\s*)([^\r\n]+)',
        '(?im)(MINIO_ROOT_PASSWORD\s*[:=]\s*)([^\r\n]+)',
        '(?im)(REDIS_PASSWORD\s*[:=]\s*)([^\r\n]+)',
        '(?im)(RABBITMQ_DEFAULT_PASS\s*[:=]\s*)([^\r\n]+)',
        '(?im)(password\s*[:=]\s*)([^\r\n]+)',
        '(?im)(secret\s*[:=]\s*)([^\r\n]+)',
        '(?im)(api[_-]?key\s*[:=]\s*)([^\r\n]+)',
        '(?im)(token\s*[:=]\s*)([^\r\n]+)'
    )

    foreach ($Pattern in $Patterns) {
        $Text = [regex]::Replace(
            $Text,
            $Pattern,
            '$1[REDACTED]'
        )
    }

    return $Text
}

function Save-Redacted {
    param(
        [string]$Path,
        [string]$Content
    )

    Write-TextFile $Path (Redact-Secrets $Content)
}

function Copy-SafeFiles {
    param(
        [string]$SourceRoot,
        [string]$DestinationRoot
    )

    $ExcludedDirectories = @(
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".next",
        "dist",
        "build",
        "_gemini_export_*",
        ".backup_*"
    )

    $ExcludedFiles = @(
        ".env",
        ".env.*",
        "*.pem",
        "*.key",
        "*.pfx",
        "*.p12",
        "*password*",
        "*secret*",
        "*credential*"
    )

    $Files = Get-ChildItem -Path $SourceRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $Full = $_.FullName

            $SkipDir = $false

            foreach ($D in $ExcludedDirectories) {
                if ($Full -like "*\$D\*" -or $Full -like "*\$D") {
                    $SkipDir = $true
                    break
                }
            }

            if ($SkipDir) {
                return $false
            }

            foreach ($F in $ExcludedFiles) {
                if ($_.Name -like $F) {
                    return $false
                }
            }

            return $true
        }

    $Count = 0

    foreach ($File in $Files) {

        try {
            $Relative = $File.FullName.Substring($SourceRoot.Length).TrimStart('\')
            $Destination = Join-Path $DestinationRoot $Relative
            $Parent = Split-Path $Destination -Parent

            if (!(Test-Path $Parent)) {
                New-Item -ItemType Directory -Path $Parent -Force | Out-Null
            }

            $TextExtensions = @(
                ".py",
                ".pyi",
                ".tsx",
                ".ts",
                ".jsx",
                ".js",
                ".json",
                ".yaml",
                ".yml",
                ".md",
                ".txt",
                ".ini",
                ".toml",
                ".sql",
                ".html",
                ".css",
                ".scss",
                ".xml",
                ".dockerfile"
            )

            if ($TextExtensions -contains $File.Extension.ToLower()) {
                $Content = Get-Content $File.FullName -Raw -ErrorAction SilentlyContinue
                Save-Redacted $Destination $Content
            }
            else {
                Copy-Item $File.FullName $Destination -Force
            }

            $Count++
        }
        catch {
        }
    }

    return $Count
}

Write-Host ""
Write-Host "============================================================"
Write-Host "PIP GEMINI EXPORT V2"
Write-Host "============================================================"
Write-Host ""
Write-Host "Project Root:"
Write-Host $ProjectRoot
Write-Host ""
Write-Host "Export:"
Write-Host $ExportRoot
Write-Host ""

# ------------------------------------------------------------
# PROJECT STRUCTURE
# ------------------------------------------------------------

$ProjectTree = Get-ChildItem $ProjectRoot -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch '\\.git\\' -and
        $_.FullName -notmatch '\\node_modules\\' -and
        $_.FullName -notmatch '\\venv\\' -and
        $_.FullName -notmatch '\\.venv\\' -and
        $_.FullName -notmatch '__pycache__' -and
        $_.FullName -notmatch '_gemini_export_'
    } |
    Select-Object FullName, Length, LastWriteTime

$ProjectTree |
    Format-Table -AutoSize |
    Out-String -Width 500 |
    Set-Content (Join-Path $ExportRoot "01_PROJECT\PROJECT_TREE.txt") -Encoding UTF8

# ------------------------------------------------------------
# SAFE SOURCE SNAPSHOT
# ------------------------------------------------------------

Write-Host "[1/8] Copying project source snapshot..."

$SourceSnapshot = Join-Path $ExportRoot "01_PROJECT\SOURCE"
New-Item -ItemType Directory -Path $SourceSnapshot -Force | Out-Null

$FileCount = Copy-SafeFiles `
    -SourceRoot $ProjectRoot `
    -DestinationRoot $SourceSnapshot

# ------------------------------------------------------------
# BACKEND
# ------------------------------------------------------------

Write-Host "[2/8] Analyzing backend..."

$BackendFiles = Get-ChildItem $ProjectRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -in @(".py",".pyi") -and
        $_.FullName -notmatch '\\venv\\' -and
        $_.FullName -notmatch '\\.venv\\' -and
        $_.FullName -notmatch '__pycache__' -and
        $_.FullName -notmatch '\\node_modules\\'
    }

$BackendReport = @()
$BackendReport += "# PIP BACKEND INVENTORY"
$BackendReport += ""
$BackendReport += "Python files: $($BackendFiles.Count)"
$BackendReport += ""

foreach ($File in $BackendFiles) {
    $Relative = $File.FullName.Substring($ProjectRoot.Length).TrimStart('\')
    $BackendReport += "- $Relative"
}

Save-Redacted `
    (Join-Path $ExportRoot "07_REPORTS\BACKEND_REPORT.md") `
    ($BackendReport -join "`r`n")

# ------------------------------------------------------------
# FRONTEND
# ------------------------------------------------------------

Write-Host "[3/8] Analyzing frontend..."

$FrontendFiles = Get-ChildItem (Join-Path $ProjectRoot "frontend") -Recurse -File -Force -ErrorAction SilentlyContinue

$FrontendReport = @()
$FrontendReport += "# PIP FRONTEND INVENTORY"
$FrontendReport += ""
$FrontendReport += "Frontend path: frontend"
$FrontendReport += "Files discovered: $($FrontendFiles.Count)"
$FrontendReport += ""

foreach ($File in $FrontendFiles) {
    $Relative = $File.FullName.Substring($ProjectRoot.Length).TrimStart('\')

    if ($Relative -notmatch '\\node_modules\\') {
        $FrontendReport += "- $Relative"
    }
}

Save-Redacted `
    (Join-Path $ExportRoot "07_REPORTS\FRONTEND_REPORT.md") `
    ($FrontendReport -join "`r`n")

# ------------------------------------------------------------
# DOCKER
# ------------------------------------------------------------

Write-Host "[4/8] Collecting Docker state..."

$DockerDir = Join-Path $ExportRoot "06_DOCKER"

$DockerVersion = Invoke-NativeSafe "docker" @("--version")
$DockerInfo = Invoke-NativeSafe "docker" @("info")
$DockerPS = Invoke-NativeSafe "docker" @("ps","-a")
$DockerImages = Invoke-NativeSafe "docker" @("images")
$DockerVolumes = Invoke-NativeSafe "docker" @("volume","ls")
$DockerNetworks = Invoke-NativeSafe "docker" @("network","ls")

Save-Redacted (Join-Path $DockerDir "docker_version.txt") $DockerVersion
Save-Redacted (Join-Path $DockerDir "docker_info.txt") $DockerInfo
Save-Redacted (Join-Path $DockerDir "docker_ps.txt") $DockerPS
Save-Redacted (Join-Path $DockerDir "docker_images.txt") $DockerImages
Save-Redacted (Join-Path $DockerDir "docker_volumes.txt") $DockerVolumes
Save-Redacted (Join-Path $DockerDir "docker_networks.txt") $DockerNetworks

$ComposeFile = Join-Path $ProjectRoot "compose.yaml"

if (Test-Path $ComposeFile) {

    $ComposeContent = Get-Content $ComposeFile -Raw
    Save-Redacted `
        (Join-Path $DockerDir "compose.yaml.redacted") `
        $ComposeContent

    $ComposeConfig = Invoke-NativeSafe "docker" @("compose","-f",$ComposeFile,"config")
    Save-Redacted `
        (Join-Path $DockerDir "docker_compose_config.txt") `
        $ComposeConfig

    $ComposeVersion = Invoke-NativeSafe "docker" @("compose","version")
    Save-Redacted `
        (Join-Path $DockerDir "docker_compose_version.txt") `
        $ComposeVersion
}

# ------------------------------------------------------------
# RUNTIME
# ------------------------------------------------------------

Write-Host "[5/8] Checking runtime..."

$Ports = @(3000,5173,8000,5432,5050,5672,15672,6379,6333,6334,9000,9001,11434)

$RuntimeReport = @()
$RuntimeReport += "# PIP RUNTIME REPORT"
$RuntimeReport += ""
$RuntimeReport += "Generated: $(Get-Date)"
$RuntimeReport += ""

foreach ($Port in $Ports) {

    try {
        $Connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

        if ($Connection) {
            $RuntimeReport += "PORT $Port = OPEN / CONFIRMED"
        }
        else {
            $RuntimeReport += "PORT $Port = CLOSED / UNAVAILABLE"
        }
    }
    catch {
        $RuntimeReport += "PORT $Port = CHECK_FAILED"
    }
}

$RuntimeReport += ""
$RuntimeReport += "## HTTP Backend"

try {
    $RootResponse = Invoke-WebRequest `
        -Uri "http://127.0.0.1:8000/" `
        -UseBasicParsing `
        -TimeoutSec 10 `
        -ErrorAction Stop

    $RuntimeReport += "HTTP STATUS = $($RootResponse.StatusCode)"
    $RuntimeReport += "BODY:"
    $RuntimeReport += $RootResponse.Content
}
catch {
    $RuntimeReport += "BACKEND HTTP CHECK FAILED"
    $RuntimeReport += $_.Exception.Message
}

Save-Redacted `
    (Join-Path $ExportRoot "07_REPORTS\RUNTIME_REPORT.md") `
    ($RuntimeReport -join "`r`n")

# ------------------------------------------------------------
# OPENAPI
# ------------------------------------------------------------

Write-Host "[6/8] Collecting OpenAPI..."

try {

    $OpenApi = Invoke-RestMethod `
        -Uri "http://127.0.0.1:8000/openapi.json" `
        -Method Get `
        -TimeoutSec 15 `
        -ErrorAction Stop

    $OpenApiJson = $OpenApi | ConvertTo-Json -Depth 100

    Write-TextFile `
        (Join-Path $ExportRoot "05_RUNTIME\OPENAPI.json") `
        $OpenApiJson

    $ApiSummary = @()
    $ApiSummary += "# PIP API SUMMARY"
    $ApiSummary += ""
    $ApiSummary += "Title: $($OpenApi.info.title)"
    $ApiSummary += "Version: $($OpenApi.info.version)"
    $ApiSummary += ""

    foreach ($Path in $OpenApi.paths.PSObject.Properties) {

        foreach ($Method in $Path.Value.PSObject.Properties) {

            if ($Method.Name -in @("get","post","put","delete","patch")) {

                $Summary = $Method.Value.summary

                if ([string]::IsNullOrWhiteSpace($Summary)) {
                    $Summary = ""
                }

                $ApiSummary += "- $($Method.Name.ToUpper()) $($Path.Name) — $Summary"
            }
        }
    }

    Write-TextFile `
        (Join-Path $ExportRoot "07_REPORTS\API_SUMMARY.md") `
        ($ApiSummary -join "`r`n")

}
catch {

    Write-TextFile `
        (Join-Path $ExportRoot "07_REPORTS\API_SUMMARY.md") `
        "# API SUMMARY`r`n`r`nOpenAPI could not be retrieved.`r`n$($_.Exception.Message)"
}

# ------------------------------------------------------------
# AI / RAG
# ------------------------------------------------------------

Write-Host "[7/8] Analyzing AI / RAG..."

$AIKeywords = @(
    "ollama",
    "langchain",
    "langgraph",
    "rag",
    "embedding",
    "qdrant",
    "vector",
    "agent",
    "llm",
    "openai",
    "model",
    "prompt",
    "retrieval"
)

$AIResults = Get-ChildItem $ProjectRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch '\\.git\\' -and
        $_.FullName -notmatch '\\node_modules\\' -and
        $_.FullName -notmatch '\\venv\\' -and
        $_.FullName -notmatch '\\.venv\\' -and
        $_.FullName -notmatch '__pycache__' -and
        $_.FullName -notmatch '_gemini_export_'
    } |
    Where-Object {
        $Name = $_.Name.ToLower()

        foreach ($Keyword in $AIKeywords) {
            if ($Name -like "*$Keyword*") {
                return $true
            }
        }

        return $false
    }

$AIReport = @()
$AIReport += "# PIP AI / RAG INVENTORY"
$AIReport += ""
$AIReport += "Potential AI/RAG related files:"
$AIReport += ""

foreach ($File in $AIResults) {
    $Relative = $File.FullName.Substring($ProjectRoot.Length).TrimStart('\')
    $AIReport += "- $Relative"
}

Save-Redacted `
    (Join-Path $ExportRoot "07_REPORTS\AI_RAG_REPORT.md") `
    ($AIReport -join "`r`n")

# ------------------------------------------------------------
# GIT
# ------------------------------------------------------------

$GitReport = @()
$GitReport += "# PIP GIT REPORT"
$GitReport += ""
$GitReport += (Invoke-NativeSafe "git" @("status","--short"))
$GitReport += ""
$GitReport += "## Branch"
$GitReport += (Invoke-NativeSafe "git" @("branch","--show-current"))
$GitReport += ""
$GitReport += "## Recent Commits"
$GitReport += (Invoke-NativeSafe "git" @("log","-10","--oneline"))

Save-Redacted `
    (Join-Path $ExportRoot "07_REPORTS\GIT_REPORT.md") `
    ($GitReport -join "`r`n")

# ------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------

$SecurityReport = @()
$SecurityReport += "# PIP SECURITY REPORT"
$SecurityReport += ""
$SecurityReport += "Sensitive files were excluded from the export."
$SecurityReport += ""
$SecurityReport += "Excluded patterns:"
$SecurityReport += "- .env"
$SecurityReport += "- .env.*"
$SecurityReport += "- *.pem"
$SecurityReport += "- *.key"
$SecurityReport += "- *.pfx"
$SecurityReport += "- *.p12"
$SecurityReport += "- password-like files"
$SecurityReport += "- secret-like files"
$SecurityReport += "- credential-like files"
$SecurityReport += ""
$SecurityReport += "Runtime reports redact detected password/token/secret values."

Write-TextFile `
    (Join-Path $ExportRoot "07_REPORTS\SECURITY_REPORT.md") `
    ($SecurityReport -join "`r`n")

# ------------------------------------------------------------
# ERROR SUMMARY
# ------------------------------------------------------------

$ErrorsReport = @()
$ErrorsReport += "# PIP ERROR / WARNING INVENTORY"
$ErrorsReport += ""
$ErrorsReport += "The following files contain likely error/warning terminology:"
$ErrorsReport += ""

$CandidateErrorFiles = Get-ChildItem $ProjectRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch '\\.git\\' -and
        $_.FullName -notmatch '\\node_modules\\' -and
        $_.FullName -notmatch '\\venv\\' -and
        $_.FullName -notmatch '\\.venv\\' -and
        $_.FullName -notmatch '_gemini_export_'
    } |
    Where-Object {
        $_.Extension.ToLower() -in @(".txt",".log",".md")
    }

foreach ($File in $CandidateErrorFiles) {

    try {
        $Content = Get-Content $File.FullName -Raw -ErrorAction SilentlyContinue

        if ($Content -match "(?i)error|exception|traceback|failed|failure|timeout|warning") {

            $Relative = $File.FullName.Substring($ProjectRoot.Length).TrimStart('\')

            $ErrorsReport += "- $Relative"
        }
    }
    catch {
    }
}

Save-Redacted `
    (Join-Path $ExportRoot "07_REPORTS\ERRORS_REPORT.md") `
    ($ErrorsReport -join "`r`n")

# ------------------------------------------------------------
# MASTER CONTEXT
# ------------------------------------------------------------

$Master = @"
# PIP AI PLATFORM — GEMINI MASTER CONTEXT

Generated: $(Get-Date)

---

## 1. PRODUCT

PIP = Project Intelligence Platform for EPC Industries.

Product type:
AI-Powered Project Management Intelligence Platform.

Target industries:
- Oil & Gas
- Petrochemical
- Steel
- Power
- Industrial Construction
- EPC

Primary objective:

Convert fragmented EPC project data into evidence-based management intelligence.

---

## 2. PRODUCT VISION

PIP is intended to become an AI Project Operating System for EPC projects.

The platform should:

- Understand project data.
- Understand project documents.
- Analyze schedule.
- Analyze risk.
- Analyze contracts.
- Monitor project health.
- Detect emerging problems.
- Generate management reports.
- Recommend corrective actions.
- Preserve project knowledge.

---

## 3. TARGET USERS

Primary users:

- Project Manager
- Planning Manager
- Project Controls Manager
- Contract Manager
- Risk Manager
- PMC
- Owner
- CEO / Executive Management

---

## 4. CORE PRODUCT MODULES

Target architecture includes:

1. Project Intelligence Core
2. AI Project Assistant
3. Document Intelligence
4. RAG / Project Knowledge
5. Schedule Intelligence
6. Risk Intelligence
7. Contract Intelligence
8. Cost Intelligence
9. Management Dashboard
10. Executive Dashboard
11. Project Control Center
12. Early Warning / Alerts
13. Multi-project management
14. Enterprise security

---

## 5. TARGET TECHNICAL ARCHITECTURE

Backend:
- Python
- FastAPI

Database:
- PostgreSQL

Vector database:
- Qdrant

Cache:
- Redis

Message queue:
- RabbitMQ

Object storage:
- MinIO

Local AI:
- Ollama
- Open-source LLMs

AI architecture:
- RAG
- Agents
- LLM orchestration

Deployment:
- Docker

Frontend:
- React / TypeScript

---

## 6. CURRENT RUNTIME SNAPSHOT

The export script checks:

- FastAPI :8000
- Frontend :5173
- Frontend :3000
- PostgreSQL :5432
- pgAdmin :5050
- RabbitMQ :5672
- RabbitMQ Management :15672
- Redis :6379
- Qdrant :6333 / :6334
- MinIO :9000 / :9001
- Ollama :11434

See:

07_REPORTS/RUNTIME_REPORT.md

---

## 7. CURRENT API SURFACE

The current FastAPI application exposes APIs for:

- Projects
- WBS
- Contracts
- Risks
- Schedule
- Schedule Import
- Cost
- Documents
- AI Chat
- Schedule Analysis
- Schedule Recovery
- Project KPI
- Project Alerts
- Project Status Report
- Project Control Center
- Project Dashboard
- AI Summary
- Executive Dashboard
- Critical Activities
- Demo

See:

05_RUNTIME/OPENAPI.json

and

07_REPORTS/API_SUMMARY.md

---

## 8. IMPORTANT ENGINEERING RULE

Do NOT assume that the original Business Plan exactly represents the current implementation.

The repository and runtime are the source of truth for the CURRENT STATE.

The Business Plan is the source of truth for the TARGET PRODUCT VISION.

Gemini must compare:

TARGET STATE vs CURRENT STATE

and identify:

- completed
- partially completed
- missing
- broken
- technically inconsistent
- architecturally risky
- redundant
- requiring refactoring

---

## 9. REQUIRED GEMINI ANALYSIS

Gemini should analyze the entire exported repository and produce:

### A. Current Architecture

Explain the actual architecture.

### B. Target Architecture

Explain the intended final PIP architecture.

### C. Gap Analysis

Create:

| Area | Target | Current | Status | Priority |
|---|---|---|---|---|

### D. Technical Debt

Identify:

- duplicated code
- architectural inconsistencies
- dead code
- temporary implementations
- weak abstractions
- security risks
- scalability risks

### E. AI/RAG Assessment

Evaluate:

- LLM integration
- Ollama
- embeddings
- Qdrant
- RAG
- context handling
- agent architecture
- hallucination control
- source attribution

### F. EPC Intelligence Assessment

Evaluate whether the platform can actually perform:

- Schedule Intelligence
- Risk Intelligence
- Contract Intelligence
- Cost Intelligence
- Project Controls
- Executive Reporting

### G. Runtime Assessment

Evaluate Docker and runtime health.

### H. Frontend/Backend Integration

Check:

- API contracts
- endpoints
- frontend calls
- timeouts
- CORS
- error handling
- loading states

### I. Security

Check:

- secrets
- authentication
- authorization
- API exposure
- tenant isolation
- document security

### J. Roadmap

Produce the shortest technically safe path from CURRENT STATE to:

PIP MVP

then:

PIP Professional

then:

PIP Enterprise

then:

AI Project Operating System

---

## 10. IMPORTANT

Do not rewrite the project blindly.

Do not rename established project folders, modules, sprints, or architecture components without a strong technical reason.

Preserve working functionality.

Prioritize:

1. Stability
2. Correctness
3. MVP completeness
4. Architecture
5. AI quality
6. Enterprise scalability
7. Optimization

---

## 11. EXPORT CONTENT

Project source snapshot:
01_PROJECT/SOURCE

Backend:
02_BACKEND

Frontend:
03_FRONTEND

AI/RAG:
04_AI_RAG

Runtime:
05_RUNTIME

Docker:
06_DOCKER

Reports:
07_REPORTS

Git:
08_GIT

Security:
09_SECURITY

---

## 12. FINAL GEMINI TASK

Act as a senior:

- Software Architect
- EPC Project Controls Expert
- AI/RAG Architect
- DevOps Engineer
- Product Architect

Analyze the exported PIP repository.

Do not merely summarize files.

Determine what PIP actually is today.

Then compare it against what PIP is supposed to become.

Return:

1. Executive Technical Assessment
2. Current Architecture
3. Target Architecture
4. Current Feature Matrix
5. Gap Analysis
6. Critical Bugs
7. Architecture Problems
8. AI/RAG Assessment
9. EPC Domain Capability Assessment
10. Security Assessment
11. Frontend/Backend Integration Assessment
12. Docker/Deployment Assessment
13. Technical Debt
14. Priority Fix List
15. Recommended Development Roadmap
16. Definition of MVP Completion
17. Definition of Professional Version
18. Definition of Enterprise Version
19. AI Project Operating System Roadmap

Every conclusion should be backed by evidence from the exported repository whenever possible.
"@

Write-TextFile `
    (Join-Path $ExportRoot "00_MASTER\00_GEMINI_START_HERE.md") `
    $Master

# Also place a copy at export root
Write-TextFile `
    (Join-Path $ExportRoot "00_GEMINI_START_HERE.md") `
    $Master

# ------------------------------------------------------------
# ZIP
# ------------------------------------------------------------

Write-Host "[8/8] Creating ZIP..."

$ZipPath = Join-Path $ProjectRoot "PIP_GEMINI_EXPORT_V2_$Timestamp.zip"

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

Compress-Archive `
    -Path (Join-Path $ExportRoot "*") `
    -DestinationPath $ZipPath `
    -CompressionLevel Optimal

Write-Host ""
Write-Host "============================================================"
Write-Host "PIP GEMINI EXPORT V2 COMPLETED"
Write-Host "============================================================"
Write-Host ""
Write-Host "Project:"
Write-Host $ProjectRoot
Write-Host ""
Write-Host "Export Directory:"
Write-Host $ExportRoot
Write-Host ""
Write-Host "Master Context:"
Write-Host (Join-Path $ExportRoot "00_GEMINI_START_HERE.md")
Write-Host ""
Write-Host "ZIP FILE:"
Write-Host $ZipPath
Write-Host ""
Write-Host "Files discovered:"
Write-Host $FileCount
Write-Host ""
Write-Host "Secrets and environment values were excluded/redacted."
Write-Host ""
Write-Host "============================================================"
