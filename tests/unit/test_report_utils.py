import os

import report_utils


def test_build_output_path_zh():
    path = report_utils.build_output_path("2026-05-10", "zh")
    assert path.endswith(os.path.join("2026", "05", "10", "geoai_world-model_dashboard_2026-05-10.md"))


def test_build_output_path_en():
    path = report_utils.build_output_path("2026-05-10", "en")
    assert path.endswith(os.path.join("2026", "05", "10", "geoai_world-model_dashboard_en_2026-05-10.md"))


def test_save_report_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(report_utils, "build_output_path", lambda date_str, language: str(tmp_path / "report.md"))
    result = report_utils.save_report("2026-05-10", "zh", "# Hello")
    assert result == str(tmp_path / "report.md")
    assert (tmp_path / "report.md").read_text(encoding="utf-8") == "# Hello"


def test_validate_and_fix_arxiv_links_fixes_incomplete():
    content = "1) Paper\n   - Link: https://arxiv.org/\n"
    papers_context = "- Title: Test\n  Link: https://arxiv.org/abs/2605.01234v1\n"
    fixed = report_utils.validate_and_fix_arxiv_links(content, papers_context)
    assert "https://arxiv.org/abs/2605.01234v1" in fixed
    assert "Link: https://arxiv.org/\n" not in fixed


def test_validate_and_fix_arxiv_links_leaves_complete():
    content = "1) Paper\n   - Link: https://arxiv.org/abs/2605.01234v1\n"
    fixed = report_utils.validate_and_fix_arxiv_links(content, "")
    assert fixed == content


def test_validate_and_fix_arxiv_links_keeps_incomplete_without_context():
    content = "1) Paper\n   - Link: https://arxiv.org/\n"
    fixed = report_utils.validate_and_fix_arxiv_links(content, "")
    assert fixed == content


def test_check_domestic_network_returns_bool():
    # We can't control network state in CI, but the function should return a bool
    result = report_utils.check_domestic_network()
    assert isinstance(result, bool)
