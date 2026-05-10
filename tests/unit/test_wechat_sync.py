from pathlib import Path

from wechat_sync import WeChatSync


def _build_sync(tmp_path: Path) -> WeChatSync:
    return WeChatSync(str(tmp_path / "config.json"))


def test_preprocess_content_normalizes_scope_and_key_message(tmp_path):
    sync = _build_sync(tmp_path)
    content = "Date: 2026-05-10\nScope: GeoAI\nKey Message: Keep it short"

    processed = sync._preprocess_content(content)

    assert "Date: 2026-05-10" not in processed
    assert "**Scope:** GeoAI" in processed
    assert "**Key Message:** Keep it short" in processed


def test_md_to_html_renders_lists_without_ul_li(tmp_path):
    sync = _build_sync(tmp_path)
    markdown = "## Section\n- First item\n- **Second** item"

    html = sync.md_to_html(markdown)

    assert "<ul" not in html
    assert "<li" not in html
    assert "First item" in html
    assert "Second" in html
    assert html.count("<p ") >= 2


def test_md_to_html_numbers_open_source_list_items(tmp_path):
    sync = _build_sync(tmp_path)
    markdown = "## Tools / Data / Open Source Updates\n- **Project A**: Useful\n- **Project B**: Also useful"

    html = sync.md_to_html(markdown)

    assert "1) Project A" in html
    assert "2) Project B" in html


def test_render_heading_line_resets_section_index_for_h2(tmp_path):
    sync = _build_sync(tmp_path)

    html, current_section, list_index = sync._render_heading_line("## Tools / Data / Open Source Updates")

    assert "<h2" in html
    assert current_section == "Tools / Data / Open Source Updates"
    assert list_index == 0


def test_md_to_html_renders_paper_title_block(tmp_path):
    sync = _build_sync(tmp_path)
    markdown = "1) **中文标题**（English Title）"

    html = sync.md_to_html(markdown)

    assert "paper_title" not in html
    assert "中文标题" in html
    assert "English Title" in html
    assert "<div" in html


def test_render_meta_line_wraps_links_in_meta_block(tmp_path):
    sync = _build_sync(tmp_path)

    html = sync._render_meta_line("Link: https://example.com/paper")

    assert 'https://example.com/paper' in html
    assert "paper_meta" not in html
    assert "<div" in html
    assert "<strong" in html


def test_render_signal_line_handles_bold_prefixed_insight(tmp_path):
    sync = _build_sync(tmp_path)

    html = sync._render_signal_line("**One-line Insight:** keep this focused")

    assert "One-line Insight" in html
    assert "keep this focused" in html
    assert "<span" in html


def test_md_to_html_routes_signal_and_link_lines_through_shared_renderers(tmp_path):
    sync = _build_sync(tmp_path)
    markdown = "- Link: https://example.com/paper\n- Impact: Stronger retrieval quality"

    html = sync.md_to_html(markdown)

    assert "https://example.com/paper" in html
    assert "Impact" in html
    assert "Stronger retrieval quality" in html
