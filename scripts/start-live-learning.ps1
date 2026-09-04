[CmdletBinding()]
param(
    [string]$Foundation = 'runs\pathway-live-20260904-123010\model-state.json',
    [string]$Resume = '',
    [ValidateRange(1, 48)] [int]$MaxRounds = 12,
    [ValidateRange(10, 86400)] [int]$MaxSeconds = 86400
)
$ErrorActionPreference = 'Stop'
$kaviRepo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$kaviFoundation = (Resolve-Path (Join-Path $kaviRepo $Foundation)).Path
$kaviStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$kaviRun = Join-Path $kaviRepo "runs\learning-live-$kaviStamp"
New-Item -ItemType Directory -Path $kaviRun | Out-Null
$kaviWindow = "KaviLearning-$kaviStamp"
$kaviRunner = "python -u -m kavi.wave_cli run --run-dir '$kaviRun' --foundation '$kaviFoundation' --max-rounds $MaxRounds --max-seconds $MaxSeconds --keep-available"
if ($Resume) {
    $kaviResume = (Resolve-Path (Join-Path $kaviRepo $Resume)).Path
    $kaviRunner += " --resume '$kaviResume'"
}
function Open-KaviLearningTab {
    param([string]$Title, [string]$Command)
    $kaviInfo = [Diagnostics.ProcessStartInfo]::new()
    $kaviInfo.FileName = (Get-Command wt.exe).Source
    $kaviInfo.UseShellExecute = $false
    $kaviArguments = @('-w', $kaviWindow, 'new-tab', '--title', $Title, '-d', $kaviRepo,
                      'powershell.exe', '-NoExit', '-Command', $Command)
    $kaviInfo.Arguments = ($kaviArguments | ForEach-Object { '"' + ([string]$_).Replace('"', '\"') + '"' }) -join ' '
    [void][Diagnostics.Process]::Start($kaviInfo)
    Start-Sleep -Milliseconds 200
}
Open-KaviLearningTab 'Kavi LIVE Teacher' $kaviRunner
foreach ($kaviChannel in @('lessons', 'answers', 'pathways', 'learning', 'grading')) {
    Open-KaviLearningTab "Kavi LIVE $kaviChannel" "python -u -m kavi.wave_cli watch --run-dir '$kaviRun' --channel $kaviChannel"
}
Open-KaviLearningTab 'Kavi LIVE Chat + Controls' "python -u -m kavi.wave_cli console --run-dir '$kaviRun'"
& wt.exe -w $kaviWindow focus-tab -t 1
Write-Output "Live run: $kaviRun"
Write-Output 'The teacher runs locally without this chat. Pause/stop remain available. No other applications were closed.'
