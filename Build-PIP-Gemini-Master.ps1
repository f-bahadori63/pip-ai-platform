$ErrorActionPreference = "Continue"

$ProjectRoot = "D:\PIP\Projects\pip-ai-platform"
$MaxBytes = 5MB
$SafeLimit = 4.8MB

Set-Location $ProjectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " PIP - FINAL GEMINI MASTER BUILDER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# Find latest Gemini export
# ------------------------------------------------------------

$Exports = Get-ChildItem $ProjectRoot -Directory -Force |
    Where-Object {
        $_.Name -like "_gemini_export_*"
    } |
    Sort-Object LastWriteTime -Descending

$LatestExport = $Exports | Select-Object -First 1

if (-not $LatestExport) {
    Write-Host "ERROR: No _gemini_export_* directory found." -ForegroundColor Red
    Write-Host "Run the PIP Gemini export script first." -ForegroundColor Yellow
    exit 1
}

Write-Host "Latest export:"
Write-Host $LatestExport.FullName -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

$OutputName = "PIP_GEMINI_MASTER_FINAL_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
$OutputPath = Join-Path $ProjectRoot $OutputName

# ------------------------------------------------------------
# Header / project definition
# ------------------------------------------------------------

$Content = New-Object System.Text.StringBuilder

[void]$Content.AppendLine("# PIP AI PLATFORM - MASTER CONTEXT FOR GEMINI")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("## IMPORTANT")
[void]$Content.AppendLine("This is the consolidated technical and product context of the PIP AI Platform.")
[void]$Content.AppendLine("Use this document as the primary source of truth for analysis, debugging, architecture review and future development.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$Content.AppendLine("Project Root: $ProjectRoot")
[void]$Content.AppendLine("Gemini Export Source: $($LatestExport.FullName)")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

[void]$Content.AppendLine("# 1. PRODUCT IDENTITY")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Product: PIP AI Platform")
[void]$Content.AppendLine("Full Name: Project Intelligence Platform for EPC Industries")
[void]$Content.AppendLine("Version: 1.0")
[void]$Content.AppendLine("Product Type: AI-Powered Project Management Intelligence Platform")
[void]$Content.AppendLine("Target Industries: Oil & Gas, Petrochemical, Steel, Power, Heavy Industry, EPC, PMC, Owner organizations")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Mission:")
[void]$Content.AppendLine("Convert scattered EPC project data into reliable management intelligence and actionable decisions.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Long-term Vision:")
[void]$Content.AppendLine("PIP should evolve into an AI Project Operating System for EPC projects.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

[void]$Content.AppendLine("# 2. BUSINESS OBJECTIVE")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("PIP is intended to become an intelligent project-control platform capable of:")
[void]$Content.AppendLine("- Understanding project documents")
[void]$Content.AppendLine("- Understanding schedule data")
[void]$Content.AppendLine("- Understanding project risks")
[void]$Content.AppendLine("- Understanding contract obligations")
[void]$Content.AppendLine("- Answering project-management questions")
[void]$Content.AppendLine("- Detecting project problems")
[void]$Content.AppendLine("- Generating management summaries")
[void]$Content.AppendLine("- Providing early warnings")
[void]$Content.AppendLine("- Reusing project knowledge")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Primary users:")
[void]$Content.AppendLine("- Project Manager")
[void]$Content.AppendLine("- Planning Manager")
[void]$Content.AppendLine("- Project Controls")
[void]$Content.AppendLine("- Contract Manager")
[void]$Content.AppendLine("- Risk Manager")
[void]$Content.AppendLine("- CEO / Owner")
[void]$Content.AppendLine("- PMC")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

[void]$Content.AppendLine("# 3. REQUIRED PRODUCT CAPABILITIES")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Core modules:")
[void]$Content.AppendLine("1. Project Intelligence Core")
[void]$Content.AppendLine("2. AI Project Assistant")
[void]$Content.AppendLine("3. Document Intelligence")
[void]$Content.AppendLine("4. RAG / Project Knowledge")
[void]$Content.AppendLine("5. Schedule Intelligence")
[void]$Content.AppendLine("6. Risk Intelligence")
[void]$Content.AppendLine("7. Contract Intelligence")
[void]$Content.AppendLine("8. Cost Intelligence")
[void]$Content.AppendLine("9. Project KPI")
[void]$Content.AppendLine("10. Project Alerts")
[void]$Content.AppendLine("11. Management Dashboard")
[void]$Content.AppendLine("12. Executive Dashboard")
[void]$Content.AppendLine("13. Project Control Center")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

[void]$Content.AppendLine("# 4. TARGET MVP")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("The MVP must be capable of accepting a real EPC project and:")
[void]$Content.AppendLine("- Reading project documents")
[void]$Content.AppendLine("- Processing contract information")
[void]$Content.AppendLine("- Processing schedule information")
[void]$Content.AppendLine("- Managing risks")
[void]$Content.AppendLine("- Answering project questions")
[void]$Content.AppendLine("- Producing project summary")
[void]$Content.AppendLine("- Producing KPI")
[void]$Content.AppendLine("- Producing alerts")
[void]$Content.AppendLine("- Producing management reports")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

[void]$Content.AppendLine("# 5. TECHNICAL ARCHITECTURE")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Backend: Python + FastAPI")
[void]$Content.AppendLine("Database: PostgreSQL")
[void]$Content.AppendLine("Vector Database: Qdrant")
[void]$Content.AppendLine("Cache: Redis")
[void]$Content.AppendLine("Message Queue: RabbitMQ")
[void]$Content.AppendLine("Object Storage: MinIO")
[void]$Content.AppendLine("Local LLM Runtime: Ollama")
[void]$Content.AppendLine("AI Architecture: RAG + Agents + LLM")
[void]$Content.AppendLine("Containerization: Docker / Docker Compose")
[void]$Content.AppendLine("Frontend: React / TypeScript ecosystem")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Hybrid AI principle:")
[void]$Content.AppendLine("Local AI is required for privacy, security and operation during internet outages.")
[void]$Content.AppendLine("Cloud AI can be added later as an optional provider.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

[void]$Content.AppendLine("# 6. ARCHITECTURE PRINCIPLES")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("- Project-centric architecture")
[void]$Content.AppendLine("- Every important entity must be associated with a project")
[void]$Content.AppendLine("- AI must use project context")
[void]$Content.AppendLine("- RAG must ground answers in project evidence")
[void]$Content.AppendLine("- AI responses should be traceable to source data")
[void]$Content.AppendLine("- Agents should be modular")
[void]$Content.AppendLine("- Local AI should remain operational without internet")
[void]$Content.AppendLine("- Backend APIs must remain usable independently from frontend")
[void]$Content.AppendLine("- Docker should provide reproducible infrastructure")
[void]$Content.AppendLine("- Security and secrets must never be committed into the project context")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

[void]$Content.AppendLine("# 7. DEVELOPMENT ROADMAP")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Phase 1: Core Platform")
[void]$Content.AppendLine("Phase 2: Document Intelligence + RAG")
[void]$Content.AppendLine("Phase 3: AI Assistant")
[void]$Content.AppendLine("Phase 4: Schedule Intelligence")
[void]$Content.AppendLine("Phase 5: Risk Intelligence")
[void]$Content.AppendLine("Phase 6: Contract Intelligence")
[void]$Content.AppendLine("Phase 7: Executive / Enterprise Dashboard")
[void]$Content.AppendLine("Phase 8: Security, deployment and production hardening")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

[void]$Content.AppendLine("# 8. CURRENT IMPLEMENTATION STATE")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("The project is not a blank prototype.")
[void]$Content.AppendLine("A working backend and infrastructure already exist.")
[void]$Content.AppendLine("The current state must be analyzed from the included reports rather than assumed.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Known confirmed runtime services:")
[void]$Content.AppendLine("- PostgreSQL")
[void]$Content.AppendLine("- pgAdmin")
[void]$Content.AppendLine("- RabbitMQ")
[void]$Content.AppendLine("- MinIO")
[void]$Content.AppendLine("- Ollama")
[void]$Content.AppendLine("- Redis")
[void]$Content.AppendLine("- Qdrant")
[void]$Content.AppendLine("- FastAPI backend on port 8000")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Frontend runtime status must be taken from RUNTIME.md / FRONTEND.md.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("---")
[void]$Content.AppendLine("")

# ------------------------------------------------------------
# Existing master context if present
# ------------------------------------------------------------

$CandidateFiles = @(
    (Join-Path $LatestExport.FullName "00_MASTER_PROMPT.md"),
    (Join-Path $LatestExport.FullName "GEMINI_CONTEXT.md"),
    (Join-Path $LatestExport.FullName "OPENAPI.json"),
    (Join-Path $LatestExport.FullName "BACKEND.md"),
    (Join-Path $LatestExport.FullName "FRONTEND.md"),
    (Join-Path $LatestExport.FullName "AI_RAG.md"),
    (Join-Path $LatestExport.FullName "DOCKER_REPORT.md"),
    (Join-Path $LatestExport.FullName "RUNTIME.md"),
    (Join-Path $LatestExport.FullName "ERRORS.md"),
    (Join-Path $LatestExport.FullName "GIT.md"),
    (Join-Path $LatestExport.FullName "SECURITY.md")
)

# Search recursively for important report files
$RecursiveCandidates = Get-ChildItem $LatestExport.FullName -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -in @(
            "00_MASTER_PROMPT.md",
            "GEMINI_CONTEXT.md",
            "OPENAPI.json",
            "BACKEND.md",
            "FRONTEND.md",
            "AI_RAG.md",
            "DOCKER_REPORT.md",
            "RUNTIME.md",
            "ERRORS.md",
            "GIT.md",
            "SECURITY.md",
            "BACKEND_REPORT.md",
            "FRONTEND_REPORT.md",
            "AI_RAG_REPORT.md",
            "DOCKER_REPORT.md",
            "RUNTIME_REPORT.md",
            "ERRORS_REPORT.md",
            "GIT_REPORT.md",
            "SECURITY_REPORT.md"
        )
    }

$AllCandidates = @($CandidateFiles + $RecursiveCandidates.FullName) |
    Where-Object { $_ -and (Test-Path $_) } |
    Select-Object -Unique

# ------------------------------------------------------------
# Add reports
# ------------------------------------------------------------

foreach ($File in $AllCandidates) {

    if (-not (Test-Path $File -PathType Leaf)) {
        continue
    }

    $Name = Split-Path $File -Leaf

    # Skip obvious secrets
    if ($Name -match '(^|\.)(env|secret|key|pem|pfx)$') {
        continue
    }

    $Bytes = (Get-Item $File).Length

    if (($Content.Length * 2) -ge $SafeLimit) {
        break
    }

    [void]$Content.AppendLine("")
    [void]$Content.AppendLine("============================================================")
    [void]$Content.AppendLine("SOURCE FILE: $Name")
    [void]$Content.AppendLine("PATH: $File")
    [void]$Content.AppendLine("SIZE: $Bytes bytes")
    [void]$Content.AppendLine("============================================================")
    [void]$Content.AppendLine("")

    try {
        $Text = Get-Content $File -Raw -ErrorAction Stop

        # Remove obvious credential values while retaining structure
        $Text = $Text -replace '(?im)(password\s*[:=]\s*)[^\s,;]+', '$1[REDACTED]'
        $Text = $Text -replace '(?im)(secret\s*[:=]\s*)[^\s,;]+', '$1[REDACTED]'
        $Text = $Text -replace '(?im)(api[_-]?key\s*[:=]\s*)[^\s,;]+', '$1[REDACTED]'
        $Text = $Text -replace '(?im)(token\s*[:=]\s*)[^\s,;]+', '$1[REDACTED]'

        [void]$Content.AppendLine($Text)
    }
    catch {
        [void]$Content.AppendLine("[Could not read this file: $($_.Exception.Message)]")
    }
}

# ------------------------------------------------------------
# Add selected project source files if space remains
# ------------------------------------------------------------

[void]$Content.AppendLine("")
[void]$Content.AppendLine("============================================================")
[void]$Content.AppendLine("SELECTED PROJECT SOURCE SNAPSHOT")
[void]$Content.AppendLine("============================================================")
[void]$Content.AppendLine("")

$SourceExtensions = @(
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".yaml",
    ".yml",
    ".json",
    ".md"
)

$ExcludedDirectories = @(
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "_gemini_export_",
    ".artifacts",
    ".backup",
    "backup_"
)

$SourceFiles = Get-ChildItem $ProjectRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $SourceExtensions -contains $_.Extension.ToLower() -and
        $_.FullName -notmatch '\\node_modules\\' -and
        $_.FullName -notmatch '\\venv\\' -and
        $_.FullName -notmatch '\\.git\\' -and
        $_.FullName -notmatch '\\__pycache__\\' -and
        $_.FullName -notmatch '\\_gemini_export_' -and
        $_.FullName -notmatch '\\\.backup' -and
        $_.FullName -notmatch '\\backup_' -and
        $_.Name -notmatch '^\.env' -and
        $_.Name -notmatch 'secret' -and
        $_.Name -notmatch 'credentials'
    } |
    Sort-Object FullName

foreach ($File in $SourceFiles) {

    $CurrentBytes = [Text.Encoding]::UTF8.GetByteCount($Content.ToString())

    if ($CurrentBytes -ge $SafeLimit) {
        break
    }

    $Remaining = $SafeLimit - $CurrentBytes

    # Do not add files larger than remaining budget
    if ($File.Length -gt $Remaining) {
        continue
    }

    try {
        $Text = Get-Content $File.FullName -Raw -ErrorAction Stop

        $Text = $Text -replace '(?im)(password\s*[:=]\s*)[^\s,;]+', '$1[REDACTED]'
        $Text = $Text -replace '(?im)(secret\s*[:=]\s*)[^\s,;]+', '$1[REDACTED]'
        $Text = $Text -replace '(?im)(api[_-]?key\s*[:=]\s*)[^\s,;]+', '$1[REDACTED]'
        $Text = $Text -replace '(?im)(token\s*[:=]\s*)[^\s,;]+', '$1[REDACTED]'

        $Block = @"

------------------------------------------------------------
SOURCE: $($File.FullName)
------------------------------------------------------------

$Text

"@

        if ([Text.Encoding]::UTF8.GetByteCount($Block) -lt $Remaining) {
            [void]$Content.Append($Block)
        }
    }
    catch {
        continue
    }
}

# ------------------------------------------------------------
# Final instructions for Gemini
# ------------------------------------------------------------

[void]$Content.AppendLine("")
[void]$Content.AppendLine("============================================================")
[void]$Content.AppendLine("FINAL INSTRUCTIONS FOR GEMINI")
[void]$Content.AppendLine("============================================================")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("You are reviewing an existing software product, not designing a project from zero.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Your responsibilities:")
[void]$Content.AppendLine("1. Understand the complete current PIP architecture.")
[void]$Content.AppendLine("2. Identify what is actually implemented versus what is only planned.")
[void]$Content.AppendLine("3. Detect architectural inconsistencies.")
[void]$Content.AppendLine("4. Detect broken or incomplete APIs.")
[void]$Content.AppendLine("5. Detect frontend/backend integration problems.")
[void]$Content.AppendLine("6. Detect Docker/runtime problems.")
[void]$Content.AppendLine("7. Evaluate AI/RAG architecture.")
[void]$Content.AppendLine("8. Evaluate the path from current implementation to production MVP.")
[void]$Content.AppendLine("9. Do not rewrite working components unnecessarily.")
[void]$Content.AppendLine("10. Preserve the existing project structure unless a change is technically justified.")
[void]$Content.AppendLine("11. Prefer incremental fixes over destructive rewrites.")
[void]$Content.AppendLine("12. Clearly distinguish FACT, OBSERVATION, INFERENCE and RECOMMENDATION.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("When proposing changes:")
[void]$Content.AppendLine("- Explain why the change is required.")
[void]$Content.AppendLine("- Identify affected files/modules.")
[void]$Content.AppendLine("- Consider backward compatibility.")
[void]$Content.AppendLine("- Consider Docker and runtime dependencies.")
[void]$Content.AppendLine("- Consider local AI/offline operation.")
[void]$Content.AppendLine("- Consider EPC domain requirements.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("Do not assume that an item is missing simply because it is not visible in one report.")
[void]$Content.AppendLine("Cross-check the consolidated context before reaching conclusions.")
[void]$Content.AppendLine("")
[void]$Content.AppendLine("============================================================")
[void]$Content.AppendLine("END OF PIP MASTER CONTEXT")
[void]$Content.AppendLine("============================================================")

# ------------------------------------------------------------
# Write UTF-8
# ------------------------------------------------------------

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($OutputPath, $Content.ToString(), $Utf8NoBom)

$Info = Get-Item $OutputPath
$SizeMB = [math]::Round($Info.Length / 1MB, 2)

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " PIP GEMINI MASTER CREATED" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "FILE:"
Write-Host $OutputPath -ForegroundColor Cyan
Write-Host ""
Write-Host "SIZE:"
Write-Host "$SizeMB MB" -ForegroundColor Yellow
Write-Host ""
Write-Host "LIMIT:"
Write-Host "5 MB maximum" -ForegroundColor Green
Write-Host ""
Write-Host "SOURCE EXPORT:"
Write-Host $LatestExport.FullName
Write-Host ""
Write-Host "This is the SINGLE FILE to upload to Gemini." -ForegroundColor Green
Write-Host ""

if ($Info.Length -gt $MaxBytes) {
    Write-Host "WARNING: File exceeded 5 MB." -ForegroundColor Red
}
else {
    Write-Host "STATUS: OK - Under 5 MB" -ForegroundColor Green
}

Write-Host ""
