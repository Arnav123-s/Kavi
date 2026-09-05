param(
    [string]$Python = 'python',
    [string]$RunDir = '',
    [string]$Config = ''
)

$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $RunDir) {
    $RunDir = Join-Path $projectRoot ('runs\circuit-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
}
if (-not $Config) {
    $Config = Join-Path $projectRoot 'curriculum\circuit-run.json'
}

Push-Location -LiteralPath $projectRoot
try {
    & $Python -u -m kavi circuit run --config $Config --run-dir $RunDir --interactive
    if ($LASTEXITCODE -ne 0) {
        throw "Circuit run ended with exit code $LASTEXITCODE. Inspect the run report."
    }
}
finally {
    Pop-Location
}
