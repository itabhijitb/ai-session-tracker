# ai-session-tracker

[![PyPI version](https://badge.fury.io/py/ai-session-tracker.svg)](https://badge.fury.io/py/ai-session-tracker)
[![Python versions](https://img.shields.io/pypi/pyversions/ai-session-tracker.svg)](https://pypi.org/project/ai-session-tracker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/itabhijitb/ai-session-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/itabhijitb/ai-session-tracker/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/itabhijitb/ai-session-tracker/branch/main/graph/badge.svg)](https://codecov.io/gh/itabhijitb/ai-session-tracker)

Unified full-text search across AI coding agent sessions (Devin, Claude Code, Cursor, Windsurf).

## Features

- **Unified Search**: Search across all your AI coding sessions from a single command
- **Fast Indexing**: SQLite FTS5 full-text search for instant results
- **Multiple Agents**: Supports Devin CLI, Claude Code, Cursor, and Windsurf
- **Deep Search**: Search inside full conversation content, not just titles
- **Time Filtering**: Filter sessions by date with natural language ("last week", "3 days ago")
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Auto-Setup**: Automatically integrates with detected agents on first run

## Installation

### From PyPI (Recommended)

```bash
pip install ai-session-tracker
```

### From Source

```bash
git clone https://github.com/itabhijitb/ai-session-tracker.git
cd ai-session-tracker
pip install -e .
```

### Using Install Scripts

```bash
# macOS/Linux
bash install.sh

# Windows
powershell -ExecutionPolicy Bypass -File install.ps1
```

The install scripts will:
1. Install the package
2. Update AGENTS.md files across detected agents
3. Build the initial search index (cold start)

## Usage

### Basic Commands

```bash
ais search "keyword"           Search across all AI agent sessions
ais search --deep "keyword"    Deep search (full conversation content)
ais search --agent devin "key" Search only Devin sessions
ais list                       List recent sessions
ais list --agent claude-code   List only Claude Code sessions
ais status                      Show detected agents
ais index                      Rebuild the search index
ais setup                      Add ais instructions to your agents' AGENTS.md
ais preview <session-id>       Preview a session without resuming
```

### Search Examples

```bash
# Search by keyword
ais search "pipeline debug"

# Deep search inside conversations
ais search --deep "config.yaml"

# Search specific agent
ais search --agent devin "IPS shuffle"

# Time-based filtering
ais search --since "last week" pipeline
ais search --since 2026-10-01 --before 2026-10-15 debug

# List sessions with filters
ais list --agent devin
ais list --dir ~/Projects/my-repo
ais list --since "3 days ago"
```

### Resume Sessions

After finding a session, use the agent-specific resume command shown in the output:

- **Devin**: `devin -r <session-id>`
- **Claude Code**: Use `/resume` inside Claude Code
- **Cursor**: Open Cursor and use session history
- **Windsurf**: Open Windsurf and use session history

## Supported Agents

| Agent | Local Storage | Resume Method |
|-------|--------------|---------------|
| Devin CLI | `~/.local/share/devin/cli/sessions.db` (SQLite) | `devin -r <session-id>` |
| Claude Code | `~/.claude/projects/<dir>/<id>.jsonl` (JSONL) | `/resume` inside Claude Code |
| Cursor | `~/Library/Application Support/Cursor/` (Mac), `%APPDATA%/Cursor` (Win) | Open Cursor session history |
| Windsurf | `~/.codeium/windsurf/` (JSON/JSONL) | Open Windsurf session history |

## Architecture

ai-session-tracker uses an **adapter pattern** where each agent has its own adapter that reads that agent's native local storage:

- **Adapters**: One adapter per agent (`devin.py`, `claude_code.py`, `cursor.py`, `windsurf.py`)
- **Unified Index**: SQLite FTS5 database aggregates sessions from all adapters
- **CLI**: Built with Click, rendered tables with Rich
- **Auto-Index**: First run automatically builds the search index from all detected agents

## Development

### Setup Development Environment

```bash
git clone https://github.com/itabhijitb/ai-session-tracker.git
cd ai-session-tracker
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
```

### Lint and Format

```bash
ruff check src/ tests/
ruff format src/ tests/
```

### Build Package

```bash
python -m build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
- Uses SQLite FTS5 for fast full-text search
- Inspired by the need to search across multiple AI coding agents
