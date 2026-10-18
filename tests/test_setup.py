"""Tests for AGENTS.md section insertion and refresh."""

from ai_session_tracker.setup import SECTION_HEADER, update_agents_md

RESUME = "**Resume**: test resume line."


def test_creates_file_with_section(tmp_path):
    path = tmp_path / "sub" / "AGENTS.md"
    assert update_agents_md(path, "# Header\n", RESUME)
    text = path.read_text()
    assert text.startswith("# Header\n")
    assert SECTION_HEADER in text
    assert "pip install ai-session-tracker" in text


def test_idempotent(tmp_path):
    path = tmp_path / "AGENTS.md"
    update_agents_md(path, "# Header\n", RESUME)
    first = path.read_text()
    assert not update_agents_md(path, "# Header\n", RESUME)
    assert path.read_text() == first


def test_replaces_stale_section_and_keeps_other_content(tmp_path):
    path = tmp_path / "AGENTS.md"
    path.write_text(
        "# Mine\n\n## Other tool\n\nkeep me\n\n"
        f"{SECTION_HEADER}\n\n**Installation**: `pip install -e ~/Projects/ai-session-tracker`\n\n"
        "## After\n\nalso keep\n"
    )
    assert update_agents_md(path, "# Header\n", RESUME)
    text = path.read_text()
    assert "~/Projects/ai-session-tracker" not in text
    assert text.count(SECTION_HEADER) == 1
    assert "keep me" in text and "## After\n\nalso keep" in text
