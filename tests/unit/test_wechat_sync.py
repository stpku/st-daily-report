"""Tests for wechat_sync module including XSS regression tests."""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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


def test_md_to_html_renders_judgments_as_summary_blocks(tmp_path):
    sync = _build_sync(tmp_path)
    markdown = (
        "## 今日判断\n"
        "今日主线: 遥感评测从泛化转向可控对照。\n"
        "- 遥感检索评测开始强调可控对照。\n"
        "今日关键词: 遥感检索 / 世界模型"
    )

    html = sync.md_to_html(markdown)

    assert "background-color: #f7fbff" in html
    assert "今日主线" in html
    assert "background-color: #fffaf2" in html
    assert "遥感检索评测开始强调可控对照" in html
    assert "今日关键词" in html
    assert "background-color: #f6f8fa" in html


def test_md_to_html_splits_original_english_title_as_subtitle(tmp_path):
    sync = _build_sync(tmp_path)
    markdown = "## A) Top Papers（精选 3-5 篇）\n1) **中文标题**（English Original Paper Title）"

    html = sync.md_to_html(markdown)

    assert "精选论文｜方法、数据与评测趋势" in html
    assert "中文标题" in html
    assert "原题：English Original Paper Title" in html


def test_build_footer_html_uses_link_footer_without_qr(tmp_path):
    config_dir = tmp_path
    (config_dir / "footer_intro.md").write_text(
        "### 继续交流\n\n[查看管理员联系方式](https://mp.weixin.qq.com/s/H79SAUA1GB0AcKUD6DSDdQ)",
        encoding="utf-8",
    )
    sync = _build_sync(config_dir)

    html = sync._build_footer_html()

    assert "查看管理员联系方式" in html
    assert "mp.weixin.qq.com/s/H79SAUA1GB0AcKUD6DSDdQ" in html
    assert "<img" not in html


# XSS regression tests for wechat_sync._process_inline
# We don't need a real config for _process_inline testing
_syncer = WeChatSync.__new__(WeChatSync)


def test_script_tag_is_escaped():
    """<script>alert(1)</script> must be escaped, not rendered."""
    result = _syncer._process_inline('<script>alert(1)</script>')
    assert '<script>' not in result
    assert '&lt;script&gt;' in result


def test_javascript_link_replaced_with_hash():
    """[click](javascript:alert(1)) must produce href='#', not javascript:."""
    result = _syncer._process_inline('[click](javascript:alert(1))')
    assert 'javascript' not in result
    assert 'href="#"' in result
    assert '>click<' in result


def test_bare_url_with_ampersand_not_double_escaped():
    """Bare URL with & in query must not produce &amp;amp;"""
    result = _syncer._process_inline('See https://example.com?a=1&b=2 for details.')
    assert '&amp;amp;' not in result
    assert 'href="https://example.com?a=1&amp;b=2"' in result


def test_link_with_ampersand_in_url():
    """Markdown link with & in URL must not double-escape."""
    result = _syncer._process_inline('[x & y](https://example.com?a=1&b=2)')
    assert '&amp;amp;' not in result
    assert 'href="https://example.com?a=1&amp;b=2"' in result
