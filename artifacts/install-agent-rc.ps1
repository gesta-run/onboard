[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ControlUrl,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ApiKey,

    [string]$InstallDir = "",

    [switch]$NoDaemon
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$entrypointUrl = if ([string]::IsNullOrWhiteSpace($env:GESTA_AGENT_INSTALLER_ENTRYPOINT_URL)) {
    "https://artifacts.gesta.run/gesta/install-agent.ps1"
} else {
    $env:GESTA_AGENT_INSTALLER_ENTRYPOINT_URL
}
$installerPath = Join-Path ([IO.Path]::GetTempPath()) "gesta-install-agent-rc-$PID.ps1"
$previousChannel = $env:GESTA_AGENT_CHANNEL

try {
    Invoke-WebRequest -UseBasicParsing -Uri $entrypointUrl -OutFile $installerPath
    $arguments = @{
        ControlUrl = $ControlUrl
        ApiKey = $ApiKey
    }
    if (-not [string]::IsNullOrWhiteSpace($InstallDir)) {
        $arguments.InstallDir = $InstallDir
    }
    if ($NoDaemon) {
        $arguments.NoDaemon = $true
    }
    $env:GESTA_AGENT_CHANNEL = "rc"
    & ([scriptblock]::Create([IO.File]::ReadAllText($installerPath))) @arguments
} finally {
    $env:GESTA_AGENT_CHANNEL = $previousChannel
    if (Test-Path -LiteralPath $installerPath) {
        Remove-Item -LiteralPath $installerPath -Force -ErrorAction SilentlyContinue
    }
}
