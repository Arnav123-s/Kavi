[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunDir
)

$ErrorActionPreference = 'Stop'
$kaviResolvedRunDir = (Resolve-Path -LiteralPath $RunDir).Path

Write-Host 'Kavi live controls'
Write-Host "  Run directory: $kaviResolvedRunDir"
Write-Host ''
Write-Host 'Type one of these commands in this tab:'
Write-Host "  python -m kavi.pathway_cli signal --run-dir '$kaviResolvedRunDir' pause"
Write-Host "  python -m kavi.pathway_cli signal --run-dir '$kaviResolvedRunDir' resume"
Write-Host "  python -m kavi.pathway_cli signal --run-dir '$kaviResolvedRunDir' stop"
Write-Host "  python -m kavi.pathway_cli signal --run-dir '$kaviResolvedRunDir' status"
Write-Host ''
Write-Host 'The finite run stops at the first failed, unavailable, or completed curriculum gate.'
