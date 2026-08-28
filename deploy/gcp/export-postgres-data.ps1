[CmdletBinding()]
param(
    [string]$LocalContainer = "pip-postgres",
    [string]$LocalDatabaseUser = "pip_user",
    [string]$LocalDatabaseName = "pip_db",
    [string]$DumpPath = ".\pip-mvp-data.sql"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or is not on PATH."
}

$running = & docker inspect `
    --format="{{.State.Running}}" `
    $LocalContainer 2>$null

if ($LASTEXITCODE -ne 0 -or $running -ne "true") {
    throw "Local PostgreSQL container '$LocalContainer' is not running."
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

$dumpFile = Get-Item $fullDumpPath

if ($dumpFile.Length -eq 0) {
    throw "The generated database dump is empty."
}

Write-Host ""
Write-Host "Database export completed successfully." -ForegroundColor Green
$dumpFile | Select-Object FullName, Length, LastWriteTime
Write-Host "Upload this SQL file to Google Cloud Shell for import." -ForegroundColor Yellow
