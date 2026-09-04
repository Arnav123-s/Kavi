[CmdletBinding()]
param(
    [ValidateRange(0, 5000)]
    [int]$IntervalMs = 250,

    [ValidateRange(0, 30)]
    [int]$StartDelaySeconds = 8,

    [ValidateRange(1, 8)]
    [int]$MaxParallelPaths = 4
)

$ErrorActionPreference = 'Stop'
$kaviRepo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$kaviStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$kaviRunDir = Join-Path $kaviRepo "runs\pathway-live-$kaviStamp"
$kaviPauseFile = Join-Path $kaviRunDir 'pause'
$kaviStopFile = Join-Path $kaviRunDir 'stop'
$kaviControlScript = Join-Path $PSScriptRoot 'show-live-controls.ps1'
New-Item -ItemType Directory -Path $kaviRunDir | Out-Null

$kaviRunner = "python -u -m kavi.pathway_cli run --run-dir '$kaviRunDir' --interval-ms $IntervalMs --start-delay-seconds $StartDelaySeconds --max-parallel-paths $MaxParallelPaths --pause-file '$kaviPauseFile' --stop-file '$kaviStopFile'"
$kaviAnswers = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel answers"
$kaviPathways = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel pathways"
$kaviLearning = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel learning"
$kaviGrading = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel grading"

$kaviTerminalArguments = @(
    '-w', 'new',
    'new-tab', '--title', 'Kavi Controller', '-d', $kaviRepo,
    'powershell.exe', '-NoExit', '-Command', $kaviRunner,
    ';',
    'new-tab', '--title', 'Kavi Answers', '-d', $kaviRepo,
    'powershell.exe', '-NoExit', '-Command', $kaviAnswers,
    ';',
    'new-tab', '--title', 'Kavi Pathways', '-d', $kaviRepo,
    'powershell.exe', '-NoExit', '-Command', $kaviPathways,
    ';',
    'new-tab', '--title', 'Kavi Learning', '-d', $kaviRepo,
    'powershell.exe', '-NoExit', '-Command', $kaviLearning,
    ';',
    'new-tab', '--title', 'Kavi Grading', '-d', $kaviRepo,
    'powershell.exe', '-NoExit', '-Command', $kaviGrading,
    ';',
    'new-tab', '--title', 'Kavi Controls', '-d', $kaviRepo,
    'powershell.exe', '-NoExit', '-File', $kaviControlScript, '-RunDir', $kaviRunDir
)

Write-Host "Opening one Windows Terminal window with six Kavi tabs."
Write-Host "Local run directory: $kaviRunDir"
Start-Process -FilePath 'wt.exe' -ArgumentList $kaviTerminalArguments -WorkingDirectory $kaviRepo
