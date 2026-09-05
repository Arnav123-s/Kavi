param(
    [string]$Python = 'python',
    [string]$RunDir = '',
    [string]$Config = ''
)

$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $RunDir) {
    $RunDir = Join-Path $projectRoot ('runs\library-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
}
if (-not $Config) {
    $Config = Join-Path $projectRoot 'curriculum\library-run.json'
}
Push-Location -LiteralPath $projectRoot
try {
    & $Python -B -m kavi.learning_window --run-dir $RunDir --config $Config
    if ($LASTEXITCODE -ne 0) { throw 'The learning window failed to start.' }
}
finally {
    Pop-Location
}
