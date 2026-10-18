"""CLI entry point — installed as `ais` command."""

from __future__ import annotations

from datetime import datetime, timedelta
import re

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ai_session_tracker.index.engine import SearchEngine
from ai_session_tracker.models import Session, SessionPreview

console = Console()

RESUME_COMMANDS = {
    "devin": "devin -r {id}",
    "claude-code": "claude --resume (use /resume in Claude Code)",
    "cursor": "Open Cursor and use session history",
    "windsurf": "Open Windsurf and use session history",
}


def _resume_hint(session: Session) -> str:
    template = RESUME_COMMANDS.get(session.agent, f"Resume using {session.agent}")
    return template.format(id=session.session_id)


def _render_table(sessions: list[Session], title: str = "Sessions"):
    if not sessions:
        console.print(Panel(
            "[yellow]No matching sessions found.[/yellow]\n\n"
            "Suggestions:\n"
            "  - Try broader keywords:  [bold]ais search pipeline[/bold]\n"
            "  - Search inside conversations:  [bold]ais search --deep \"exact phrase\"[/bold]\n"
            "  - Rebuild the index:  [bold]ais index[/bold]\n"
            "  - Check detected agents:  [bold]ais status[/bold]",
            title="No Results",
            border_style="yellow",
        ))
        return

    from pathlib import Path
    home = str(Path.home())

    t = Table(title=title, show_lines=False, pad_edge=False)
    t.add_column("#", style="bold yellow", no_wrap=True)
    t.add_column("Agent", style="cyan", no_wrap=True)
    t.add_column("Session ID", style="bold", no_wrap=True)
    t.add_column("Directory")
    t.add_column("Title / First Prompt")
    t.add_column("Started", no_wrap=True)

    for i, s in enumerate(sessions):
        marker = ">>>" if i == 0 else str(i + 1)

        display = s.title or s.first_prompt or "(untitled)"
        if len(display) > 35:
            display = display[:35] + ".."

        d = s.directory
        if d.startswith(home):
            d = "~" + d[len(home):]
        if len(d) > 40:
            d = ".." + d[-38:]

        row_style = "bold" if i == 0 else ""
        t.add_row(
            marker,
            s.agent,
            s.session_id[:20],
            d,
            display,
            s.start_time[:19] if s.start_time else "",
            style=row_style,
        )
    console.print(t)

    latest = sessions[0]
    console.print()
    console.print(f"  [bold yellow]>>>[/bold yellow] = most recent session")
    console.print(f"  [bold]To resume latest:[/bold] [green]{_resume_hint(latest)}[/green]")
    console.print(f"  [dim]To resume any other: replace the session ID in the command above[/dim]")


def _parse_date(value: str) -> str | None:
    v = value.strip().lower()
    now = datetime.now()

    if v == "today":
        return now.strftime("%Y-%m-%d")
    if v == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    if v == "last week":
        return (now - timedelta(weeks=1)).strftime("%Y-%m-%d")
    if v == "last month":
        return (now - timedelta(days=30)).strftime("%Y-%m-%d")

    m = re.match(r"(\d+)\s+(day|week|month)s?\s+ago", v)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if unit == "day":
            return (now - timedelta(days=n)).strftime("%Y-%m-%d")
        elif unit == "week":
            return (now - timedelta(weeks=n)).strftime("%Y-%m-%d")
        elif unit == "month":
            return (now - timedelta(days=n * 30)).strftime("%Y-%m-%d")

    if re.match(r"\d{4}-\d{2}-\d{2}", v):
        return v[:10]

    return None


def _filter_by_time(sessions: list[Session], since: str | None, before: str | None) -> list[Session]:
    filtered = sessions
    if since:
        since_date = _parse_date(since)
        if since_date:
            filtered = [s for s in filtered if s.start_time[:10] >= since_date]
    if before:
        before_date = _parse_date(before)
        if before_date:
            filtered = [s for s in filtered if s.start_time[:10] <= before_date]
    return filtered


def _auto_index_if_empty(engine: SearchEngine) -> bool:
    sessions = engine.list_sessions(limit=1)
    if sessions:
        return False
    console.print("[dim]First run detected — building index from all agents...[/dim]")
    counts = engine.reindex()
    total = sum(counts.values())
    if total > 0:
        console.print(f"[green]Indexed {total} sessions.[/green]\n")
    else:
        console.print(
            "[yellow]No sessions found. Make sure you have at least one AI agent "
            "(Devin, Claude Code, Cursor, or Windsurf) installed and have used it.[/yellow]\n"
        )
    return True


@click.group()
@click.version_option(package_name="ai-session-tracker")
def main():
    """ais — Find any past AI coding session in seconds.

    Works across Devin, Claude Code, Cursor, and Windsurf.
    Searches session titles, first prompts, and (with --deep) full conversations.

    Quick start:

      ais search "pipeline debug"      Find sessions by keyword

      ais preview <session-id>         See what happened in a session

      ais list --since "last week"     Recent sessions with time filter

      ais status                       See which agents are detected

    """
    # Run setup on first invocation (cold start)
    from pathlib import Path
    setup_flag = Path.home() / ".config" / "ai-session-tracker" / ".setup_complete"
    if not setup_flag.exists():
        setup_flag.parent.mkdir(parents=True, exist_ok=True)
        try:
            from ai_session_tracker.setup import setup_agents
            setup_agents()
            setup_flag.touch()
        except Exception:
            pass  # Non-critical, continue


@main.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--agent", "-a", default=None,
              help="Only search one agent: devin, claude-code, cursor, or windsurf")
@click.option("--deep", "-d", is_flag=True,
              help="Search inside full conversations, not just titles (slower but thorough)")
@click.option("--since", "-s", default=None,
              help='Only show sessions after this date: "2026-10-01", "last week", "3 days ago"')
@click.option("--before", "-b", default=None,
              help='Only show sessions before this date: "2026-10-01", "yesterday"')
@click.option("--limit", "-n", default=30, help="Maximum number of results to show")
def search(query: tuple[str, ...], agent: str | None, deep: bool,
           since: str | None, before: str | None, limit: int):
    """Search your AI coding sessions by keyword.

    Searches session titles and first prompts. If nothing is found, automatically
    searches inside full conversation content as a fallback.

    \b
    Examples:
      ais search pipeline debug
      ais search --deep "config.yaml"
      ais search --agent devin "IPS shuffle"
      ais search --since "last week" pipeline
      ais search --since 2026-10-01 --before 2026-10-15 debug
    """
    q = " ".join(query)
    engine = SearchEngine()
    _auto_index_if_empty(engine)

    if deep:
        results = engine.deep_search(q, agent=agent, limit=limit)
        title = f"Results for '{q}' (full conversation search)"
    else:
        results = engine.search(q, agent=agent, limit=limit)
        if not results:
            results = engine.deep_search(q, agent=agent, limit=limit)
            if results:
                console.print(
                    "[dim]No match in titles — searched inside full conversations instead.[/dim]\n"
                )
        title = f"Results for '{q}'"

    if since or before:
        results = _filter_by_time(results, since, before)
        if since:
            title += f" (since {_parse_date(since)})"
        if before:
            title += f" (before {_parse_date(before)})"

    _render_table(results, title=title)


@main.command(name="list")
@click.option("--agent", "-a", default=None,
              help="Only list one agent: devin, claude-code, cursor, or windsurf")
@click.option("--dir", "-d", "directory", default=None,
              help="Only show sessions from this folder (partial match works)")
@click.option("--since", "-s", default=None,
              help='Only show sessions after this date: "2026-10-01", "last week", "3 days ago"')
@click.option("--before", "-b", default=None,
              help='Only show sessions before this date: "2026-10-01", "yesterday"')
@click.option("--limit", "-n", default=30, help="Maximum number of results to show")
def list_sessions(agent: str | None, directory: str | None,
                  since: str | None, before: str | None, limit: int):
    """List your recent AI coding sessions.

    Shows the most recent sessions across all agents, newest first.

    \b
    Examples:
      ais list
      ais list --agent devin
      ais list --dir ~/Projects/my-repo
      ais list --since "last week"
      ais list --since "3 days ago" --agent devin
    """
    engine = SearchEngine()
    _auto_index_if_empty(engine)
    results = engine.list_sessions(agent=agent, directory=directory, limit=limit)
    title = "Recent Sessions"
    if since or before:
        results = _filter_by_time(results, since, before)
        if since:
            title += f" (since {_parse_date(since)})"
        if before:
            title += f" (before {_parse_date(before)})"
    _render_table(results, title=title)


@main.command()
@click.argument("session_id", required=True)
@click.option("--agent", "-a", default=None,
              help="Specify the agent if session ID exists in multiple agents")
@click.option("--messages", "-m", default=20,
              help="Number of conversation turns to show (default: 20)")
def preview(session_id: str, agent: str | None, messages: int):
    """Preview what happened in a session without resuming it.

    Shows the conversation flow: what you asked and what the agent answered.

    \b
    Examples:
      ais preview pewter-snowshoe
      ais preview --agent devin harmonious-sync
      ais preview --messages 50 pewter-snowshoe
    """
    engine = SearchEngine()
    result = engine.preview(session_id, agent=agent)

    if not result:
        console.print(Panel(
            f"[yellow]Session '{session_id}' not found.[/yellow]\n\n"
            "Suggestions:\n"
            f"  - Check the ID: [bold]ais search \"{session_id[:10]}\"[/bold]\n"
            "  - Specify the agent: [bold]ais preview --agent devin <id>[/bold]\n"
            "  - Rebuild the index: [bold]ais index[/bold]",
            title="Session Not Found",
            border_style="yellow",
        ))
        return

    from pathlib import Path
    home = str(Path.home())
    d = result.directory
    if d.startswith(home):
        d = "~" + d[len(home):]

    console.print(Panel(
        f"[bold]Session:[/bold] {result.session_id}\n"
        f"[bold]Agent:[/bold] {result.agent}\n"
        f"[bold]Directory:[/bold] {d}\n"
        f"[bold]Title:[/bold] {result.title or '(untitled)'}\n"
        f"[bold]Started:[/bold] {result.start_time}\n"
        f"[bold]Messages:[/bold] {result.total_messages} total "
        f"({len(result.user_messages)} from you, {len(result.assistant_messages)} from agent)",
        title="Session Info",
        border_style="blue",
    ))

    console.print()
    shown = 0
    for msg in result.messages:
        text = msg.short_content
        if not text:
            continue
        if shown >= messages:
            remaining = result.total_messages - shown
            if remaining > 0:
                console.print(f"\n[dim]... {remaining} more messages. "
                              f"Use --messages {result.total_messages} to see all.[/dim]")
            break

        if msg.role == "user":
            console.print(f"\n  [bold cyan]You:[/bold cyan] {text}")
        else:
            console.print(f"\n  [bold green]Agent:[/bold green] {text}")
        shown += 1

    console.print()
    hint = _resume_hint(Session(
        session_id=result.session_id, agent=result.agent, directory=result.directory))
    console.print(f"  [bold]To resume:[/bold] [green]{hint}[/green]")


@main.command()
def status():
    """Check which AI agents are installed and how many sessions each has.

    \b
    Example:
      ais status
    """
    engine = SearchEngine()

    t = Table(title="Detected AI Agents", show_lines=False)
    t.add_column("Agent", style="bold", width=15)
    t.add_column("Installed?", width=12)
    t.add_column("Sessions", justify="right", width=10)
    t.add_column("Where it stores data", width=50)

    agent_paths = {
        "devin": "~/.local/share/devin/cli/sessions.db",
        "claude-code": "~/.claude/projects/**/*.jsonl",
        "cursor": "~/Library/Application Support/Cursor/ (Mac) or %APPDATA%\\Cursor (Win)",
        "windsurf": "~/.codeium/windsurf/",
    }

    for s in engine.status():
        available = "[green]yes[/green]" if s["available"] else "[red]no[/red]"
        path = agent_paths.get(s["agent"], "unknown")
        t.add_row(s["agent"], available, str(s["sessions"]), f"[dim]{path}[/dim]")

    console.print(t)
    console.print()
    console.print("[dim]Agents marked 'no' are either not installed or have no session history yet.[/dim]")


@main.command()
def index():
    """Rebuild the search index from all installed agents.

    Run this after installing a new agent, or if search results seem incomplete.
    This reads each agent's session data and builds a unified search index.

    \b
    Example:
      ais index
    """
    engine = SearchEngine()
    with console.status("[bold]Reading sessions from all agents..."):
        counts = engine.reindex()

    t = Table(title="Index Complete", show_lines=False)
    t.add_column("Agent", style="bold", width=15)
    t.add_column("Sessions Found", justify="right", width=18)

    total = 0
    for agent_name, count in counts.items():
        t.add_row(agent_name, str(count))
        total += count
    t.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")

    console.print(t)
    console.print(f"\n[dim]Index saved to: {engine.db_path}[/dim]")

    if total == 0:
        console.print(
            "\n[yellow]No sessions found. Make sure you have used at least one "
            "supported agent (Devin, Claude Code, Cursor, or Windsurf).[/yellow]"
        )
    else:
        console.print(f"\n[green]Ready! Try:[/green] ais search \"your keyword\"")


if __name__ == "__main__":
    main()
