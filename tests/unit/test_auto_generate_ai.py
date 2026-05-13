import auto_generate_ai
import report_prompting


def test_auto_generate_ai_reexports_core_utilities():
    assert callable(auto_generate_ai.generate_content)
    assert callable(auto_generate_ai.validate_and_fix_arxiv_links)
    assert callable(auto_generate_ai.save_report)
    assert callable(auto_generate_ai.check_domestic_network)


def test_build_output_path_uses_language_specific_filename():
    zh_path = auto_generate_ai.build_output_path("2026-05-10", "zh")
    en_path = auto_generate_ai.build_output_path("2026-05-10", "en")

    assert zh_path.endswith("2026\\05\\10\\geoai_world-model_dashboard_2026-05-10.md")
    assert en_path.endswith("2026\\05\\10\\geoai_world-model_dashboard_en_2026-05-10.md")


def test_validate_and_fix_arxiv_links_fixes_incomplete_link():
    content = "1) Paper\n   - Link: https://arxiv.org/\n"
    papers_context = (
        "- Title: Test Paper\n"
        "  Link: https://arxiv.org/abs/2605.01234v1\n"
    )

    fixed, unresolved = auto_generate_ai.validate_and_fix_arxiv_links(content, papers_context)

    assert "https://arxiv.org/abs/2605.01234v1" in fixed
    assert "Link: https://arxiv.org/\n" not in fixed
    assert unresolved == 0


def test_validate_and_fix_arxiv_links_leaves_complete_link_unchanged():
    content = "1) Paper\n   - Link: https://arxiv.org/abs/2605.01234v1\n"
    papers_context = ""

    fixed, unresolved = auto_generate_ai.validate_and_fix_arxiv_links(content, papers_context)

    assert fixed == content
    assert unresolved == 0


def test_validate_and_fix_arxiv_links_keeps_incomplete_link_when_no_context():
    content = "1) Paper\n   - Link: https://arxiv.org/\n"

    fixed, unresolved = auto_generate_ai.validate_and_fix_arxiv_links(content, "")

    assert fixed == content
    assert unresolved == 1
