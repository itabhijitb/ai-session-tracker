# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of ai-session-tracker
- Unified search across Devin CLI, Claude Code, Cursor, and Windsurf
- SQLite FTS5 full-text search index
- Deep search inside full conversation content
- Time-based filtering with natural language dates
- Auto-setup on first run (updates AGENTS.md across detected agents)
- Cold start indexing during installation
- Cross-platform support (macOS, Linux, Windows)
- CLI with rich table output
- Session preview functionality
- Agent-specific resume commands

### Features
- Adapter pattern for extensible agent support
- Platform-aware path resolution
- Auto-fallback from title search to deep search
- Minimum 3-char guard on deep search to prevent false positives
- `>>>` marker on most recent session in results
- Installation scripts for all platforms

## [0.1.0] - 2026-10-18

### Added
- Initial public release
- Support for Devin CLI sessions
- Support for Claude Code sessions
- Support for Cursor sessions
- Support for Windsurf sessions
- Unified SQLite FTS5 search index
- CLI commands: search, list, preview, status, index
- Auto-index on first run
- Installation scripts (install.sh, install.ps1)
- AGENTS.md integration with detected agents
