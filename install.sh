#!/usr/bin/env bash
set -euo pipefail

echo "=== ai-session-tracker installer ==="
echo ""

PYTHON=${PYTHON:-python3}
PY_VER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10+ required (found $PY_VER)"
    exit 1
fi
echo "[ok] Python $PY_VER"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    echo "[..] Installing from local source..."
    $PYTHON -m pip install "$SCRIPT_DIR" --quiet
else
    echo "[..] Installing from PyPI..."
    $PYTHON -m pip install ai-session-tracker --quiet
fi
echo "[ok] Package installed"

if command -v ais &>/dev/null; then
    echo "[ok] 'ais' command available"
else
    AIS_PATH=$($PYTHON -c "import sysconfig; print(sysconfig.get_path('scripts'))")/ais
    if [ -f "$AIS_PATH" ]; then
        echo "[!!] 'ais' installed at $AIS_PATH but not in PATH"
        echo "     Add this to your shell profile:"
        echo "     export PATH=\"$($PYTHON -c 'import sysconfig; print(sysconfig.get_path("scripts"))'):\$PATH\""
    else
        echo "[!!] 'ais' command not found in PATH. You may need to restart your shell."
    fi
fi

echo ""
echo "[..] Updating AGENTS.md across detected agents..."
$PYTHON -m ai_session_tracker.setup 2>/dev/null || true
echo ""

echo "[..] Building initial index (cold start)..."
ais index 2>/dev/null || $PYTHON -m ai_session_tracker.cli index
echo ""
echo "[ok] Setup complete!"
echo ""
echo "Usage:"
echo "  ais search 'keyword'        Search across all AI agent sessions"
echo "  ais search -d 'keyword'     Deep search (full conversation content)"
echo "  ais search -a devin 'key'   Search only Devin sessions"
echo "  ais list                    List recent sessions"
echo "  ais list -a claude-code     List only Claude Code sessions"
echo "  ais status                  Show detected agents"
echo "  ais index                   Rebuild the search index"
