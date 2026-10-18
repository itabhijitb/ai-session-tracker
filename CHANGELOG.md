# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-18

### Added
- Initial public release
- Unified search across Devin CLI, Claude Code, Cursor, and Windsurf sessions
- SQLite FTS5 full-text search index, with auto-fallback to deep (full conversation) search
- Time-based filtering with natural language dates ("last week", "3 days ago", ISO dates)
- CLI commands: search, list, preview, status, index, setup
- `ais setup` (also run by the install scripts) adds or refreshes an `ais` section in
  `~/.claude/AGENTS.md` and `~/.config/devin/AGENTS.md`
- Index is built on first run and refreshed automatically when older than 5 minutes
- `ais preview` accepts the truncated session IDs shown in result tables
- `>>>` marker on the most recent session and agent-specific resume hints
- Installation scripts (install.sh, install.ps1); cross-platform path resolution

### Fixed
- Timestamps from different agents (UTC ISO, local SQLite, epoch millis) are normalized to
  local time, so "most recent" ordering and `--since`/`--before` filters are correct
- Claude Code session directories containing `-` are no longer shown as `/`
