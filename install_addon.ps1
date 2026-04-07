# Installs plugin.video.onedriveshare into the current user's Kodi addons folder (Windows).
# Run once, then restart Kodi. Edit PROXY_URL in resources\lib\config.py after install if needed,
# or re-run after changing it in the repo and downloading again.
$ErrorActionPreference = 'Stop'
$RepoBase = 'https://raw.githubusercontent.com/ghemed/kodi-setup/main/plugin.video.onedriveshare'
$Root = Join-Path $env:APPDATA 'Kodi\addons\plugin.video.onedriveshare'
$Paths = @(
  'addon.xml',
  'addon.py',
  'resources/settings.xml',
  'resources/__init__.py',
  'resources/lib/__init__.py',
  'resources/lib/config.py'
)
Write-Host "Installing OneDrive Share addon to:`n  $Root"
foreach ($p in $Paths) {
  $out = Join-Path $Root $p
  $dir = Split-Path -Parent $out
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $uri = $RepoBase + '/' + ($p -replace '\\', '/')
  Invoke-WebRequest -Uri $uri -OutFile $out -UseBasicParsing
}
Write-Host "Done. Restart Kodi, then open Add-ons -> Video add-ons -> OneDrive Share."
