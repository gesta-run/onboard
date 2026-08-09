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

$channel = if ([string]::IsNullOrWhiteSpace($env:GESTA_AGENT_CHANNEL)) {
    "stable"
} else {
    $env:GESTA_AGENT_CHANNEL
}
$rcVersion = "0.0.1-rc83"
$stableVersion = "0.1.0"

switch ($channel) {
    "rc" { $version = $rcVersion }
    "stable" { $version = $stableVersion }
    default { throw "Unsupported GESTA_AGENT_CHANNEL: $channel. Supported channels: rc, stable." }
}
if ([string]::IsNullOrWhiteSpace($version)) {
    throw "No $channel agent release is published."
}
if (-not [regex]::IsMatch($version, '^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$')) {
    throw "Invalid $channel agent release version: $version."
}

$channelUrl = if ([string]::IsNullOrWhiteSpace($env:GESTA_AGENT_INSTALL_BASE_URL)) {
    "https://artifacts.gesta.run/gesta/agent/$channel"
} else {
    $env:GESTA_AGENT_INSTALL_BASE_URL.TrimEnd("/")
}
$baseUrl = "$channelUrl/$version"
$installerPath = Join-Path ([IO.Path]::GetTempPath()) "gesta-install-agent-$PID.ps1"

try {
    Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/install-agent.ps1" -OutFile $installerPath
    $arguments = @{
        ControlUrl = $ControlUrl
        ApiKey = $ApiKey
        BaseUrl = $baseUrl
    }
    if (-not [string]::IsNullOrWhiteSpace($InstallDir)) {
        $arguments.InstallDir = $InstallDir
    }
    if ($NoDaemon) {
        $arguments.NoDaemon = $true
    }
    & ([scriptblock]::Create([IO.File]::ReadAllText($installerPath))) @arguments
} finally {
    if (Test-Path -LiteralPath $installerPath) {
        Remove-Item -LiteralPath $installerPath -Force -ErrorAction SilentlyContinue
    }
}
