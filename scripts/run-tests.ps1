param(
    [ValidateSet('ui', 'api', 'unit', 'report', 'serve')][string]$Suite = 'ui',
    [ValidateSet('chrome', 'firefox')][string]$Browser = 'chrome',
    [string]$Tags = '@smoke',
    [ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$RunName = 'local',
    [switch]$LocalBrowser
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    if (Test-Path -LiteralPath '.env') {
        foreach ($line in Get-Content -LiteralPath '.env') {
            if ($line -match '^\s*#' -or [string]::IsNullOrWhiteSpace($line)) { continue }
            $parts = $line -split '=', 2
            if ($parts.Count -ne 2 -or $parts[0] -notmatch '^[A-Z][A-Z0-9_]*$') { throw 'Invalid .env assignment' }
            [Environment]::SetEnvironmentVariable($parts[0], $parts[1].Trim().Trim('"').Trim("'"), 'Process')
        }
    }
    if (-not $env:JAVA_HOME -and (Test-Path -LiteralPath '.tools\jdk-17.0.13+11\bin\java.exe')) {
        $env:JAVA_HOME = Join-Path $projectRoot '.tools\jdk-17.0.13+11'
    }
    if (-not $env:JAVA_HOME) { throw 'Set JAVA_HOME to your Java 17 JDK.' }
    $env:PATH = (Join-Path $env:JAVA_HOME 'bin') + ';' + $env:PATH
    $env:BROWSER_BASE_URL = 'http://app/web/index.php'
    $env:GRID_URL = 'http://localhost:4444'
    if ($LocalBrowser) { $env:BROWSER_BASE_URL = $env:BASE_URL; $env:GRID_URL = '' }
    $buildDirectory = 'target/runs/' + $RunName
    $mavenArguments = @('-B', '-ntp', ('-Dbuild.dir=' + $buildDirectory))
    if ($Suite -eq 'report' -or $Suite -eq 'serve') {
        $mavenArguments += 'allure:' + $Suite
    } else {
        $mavenArguments += @('test', ('-Dsuite=' + $Suite), ('-Dbrowser=' + $Browser), '-Dworkers=1')
        if ($Suite -eq 'api') { $mavenArguments += '-Papi' }
        if ($Suite -eq 'ui') {
            $mavenArguments += @(
                ('-Dcucumber.filter.tags=' + $Tags),
                ('-Dcucumber.plugin=pretty,json:' + $buildDirectory + '/cucumber.json,io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm')
            )
        }
    }
    & '.\mvnw.cmd' @mavenArguments
    $testExit = $LASTEXITCODE
} finally { Pop-Location }
exit $testExit
