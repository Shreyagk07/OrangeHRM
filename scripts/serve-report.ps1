param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$RunName,
    [ValidateRange(1024,65535)][int]$Port = 8765
)
$ErrorActionPreference = 'Stop'
$reportPath = Join-Path (Split-Path $PSScriptRoot -Parent) "target\runs\$RunName\site\allure-maven-plugin"
if (-not (Test-Path -LiteralPath (Join-Path $reportPath 'index.html'))) { throw 'Generate the Allure report first.' }
Write-Host "Open http://127.0.0.1:$Port/ ; Ctrl+C stops this report server."
# Serve the existing report; do not generate another temporary Allure copy.
python -m http.server $Port --bind 127.0.0.1 --directory $reportPath
exit $LASTEXITCODE
