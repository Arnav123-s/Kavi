param(
    [string]$Python = 'python',
    [string]$RunDir = '',
    [string]$Config = '',
    [switch]$Start
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
    $windowArgs = @('-B', '-m', 'kavi.learning_window', '--run-dir', $RunDir, '--config', $Config)
    if ($Start) { $windowArgs += '--start' }
    & $Python @windowArgs
    if ($LASTEXITCODE -ne 0) { throw 'The learning window failed to start.' }
}
finally {
    Pop-Location
}
