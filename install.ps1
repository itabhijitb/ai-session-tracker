# ai-session-tracker installer for Windows
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "=== ai-session-tracker installer ===" -ForegroundColor Cyan
Write-Host ""

try {
    $pyVer = python --version 2>&1
    Write-Host "[ok] $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path "$scriptDir\pyproject.toml") {
    Write-Host "[..] Installing from local source..."
    python -m pip install $scriptDir --quiet
} else {
    Write-Host "[..] Installing from PyPI..."
    python -m pip install ai-session-tracker --quiet
}
Write-Host "[ok] Package installed" -ForegroundColor Green

$aisPath = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
if (Get-Command ais -ErrorAction SilentlyContinue) {
    Write-Host "[ok] 'ais' command available" -ForegroundColor Green
} else {
    Write-Host "[!!] 'ais' installed at $aisPath but not in PATH" -ForegroundColor Yellow
    Write-Host "     Add to PATH: $aisPath"
}

Write-Host ""
Write-Host "[..] Updating AGENTS.md across detected agents..."
try {
    python -m ai_session_tracker.setup
} catch {
    # Non-critical, continue
}

Write-Host ""
Write-Host "[..] Building initial index (cold start)..."
try {
    ais index
} catch {
    python -m ai_session_tracker.cli index
}

Write-Host ""
Write-Host "[ok] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:"
Write-Host "  ais search 'keyword'        Search across all AI agent sessions"
Write-Host "  ais search -d 'keyword'     Deep search (full conversation content)"
Write-Host "  ais list                    List recent sessions"
Write-Host "  ais status                  Show detected agents"
Write-Host "  ais index                   Rebuild the search index"
