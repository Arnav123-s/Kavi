[CmdletBinding()]
param(
    [ValidateRange(0, 5000)]
    [int]$IntervalMs = 250,

    [ValidateRange(0, 30)]
    [int]$StartDelaySeconds = 8,

    [ValidateRange(1, 8)]
    [int]$MaxParallelPaths = 4,

    [switch]$AutoTeach
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
if ($AutoTeach) { $kaviRunner += ' --auto-teach' }
$kaviTeaching = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel lessons"
$kaviAnswers = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel answers"
$kaviPathways = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel pathways"
$kaviLearning = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel learning"
$kaviGrading = "python -u -m kavi.pathway_cli watch --run-dir '$kaviRunDir' --channel grading"

function Start-KaviTerminalTab {
    param(
        [Parameter(Mandatory = $true)] [string]$WindowName,
        [Parameter(Mandatory = $true)] [string]$Title,
        [Parameter(Mandatory = $true)] [string[]]$CommandArguments
    )

    $kaviStartInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $kaviStartInfo.FileName = (Get-Command 'wt.exe').Source
    $kaviStartInfo.UseShellExecute = $false
    $kaviAllArguments = @(
        '-w', $WindowName, 'new-tab', '--title', $Title, '-d', $kaviRepo,
        'powershell.exe', '-NoExit'
    )
    $kaviAllArguments += $CommandArguments
    $kaviStartInfo.Arguments = ($kaviAllArguments | ForEach-Object {
        '"' + ([string]$_).Replace('"', '\"') + '"'
    }) -join ' '
    [void][System.Diagnostics.Process]::Start($kaviStartInfo)
    Start-Sleep -Milliseconds 250
}

Write-Host "Opening one Windows Terminal window with seven Kavi tabs."
Write-Host "Local run directory: $kaviRunDir"
$kaviWindowName = "KaviPathways-$kaviStamp"
Start-KaviTerminalTab -WindowName $kaviWindowName -Title 'Kavi Controller' -CommandArguments @('-Command', $kaviRunner)
Start-KaviTerminalTab -WindowName $kaviWindowName -Title 'Kavi Teaching' -CommandArguments @('-Command', $kaviTeaching)
Start-KaviTerminalTab -WindowName $kaviWindowName -Title 'Kavi Answers' -CommandArguments @('-Command', $kaviAnswers)
Start-KaviTerminalTab -WindowName $kaviWindowName -Title 'Kavi Pathways' -CommandArguments @('-Command', $kaviPathways)
Start-KaviTerminalTab -WindowName $kaviWindowName -Title 'Kavi Learning' -CommandArguments @('-Command', $kaviLearning)
Start-KaviTerminalTab -WindowName $kaviWindowName -Title 'Kavi Grading' -CommandArguments @('-Command', $kaviGrading)
Start-KaviTerminalTab -WindowName $kaviWindowName -Title 'Kavi Controls' -CommandArguments @('-File', $kaviControlScript, '-RunDir', $kaviRunDir)

& wt.exe -w $kaviWindowName focus-tab -t 1
