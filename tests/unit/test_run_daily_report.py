import run_daily_report


def test_resolve_target_date_prefers_cli_argument():
    assert run_daily_report.resolve_target_date(["run_daily_report.py", "2026-05-10"]) == "2026-05-10"


def test_build_news_context_formats_multiple_items():
    news_context = run_daily_report.build_news_context(
        [
            {
                "title": "Item A",
                "date": "2026-05-10",
                "url": "https://example.com/a",
                "summary": "alpha",
            },
            {
                "title": "Item B",
                "date": "2026-05-09",
                "url": "https://example.com/b",
                "summary": "beta",
            },
        ]
    )

    assert "- Title: Item A" in news_context
    assert "URL: https://example.com/b" in news_context
    assert news_context.endswith("\n")


def test_build_news_context_uses_fallback_when_empty():
    news_context = run_daily_report.build_news_context([])

    assert news_context == "No specific news found. Please search for general recent updates in Spatial Intelligence."


def test_generate_and_save_report_runs_fix_and_save(monkeypatch):
    calls = []
    validation_calls = []

    monkeypatch.setattr(
        run_daily_report.auto_generate_ai,
        "generate_content",
        lambda config, target_date, papers_context, news_context, language: "raw-content",
    )
    monkeypatch.setattr(
        run_daily_report.auto_generate_ai,
        "validate_and_fix_arxiv_links",
        lambda content, papers_context: (f"fixed::{content}::{papers_context}", 0),
    )
    monkeypatch.setattr(
        run_daily_report.daily_report_quality,
        "clean_markdown_artifacts",
        lambda content: f"clean::{content}",
    )

    class FakeValidation:
        warnings = []
        blockers = []
        ok = True

        def to_dict(self):
            return {"ok": True}

    def fake_validate(content, target_date, language):
        validation_calls.append((content, target_date, language))
        return FakeValidation()

    monkeypatch.setattr(run_daily_report.daily_report_quality, "validate_report", fake_validate)

    def fake_save(date_str, language, content):
        calls.append((date_str, language, content))
        return f"/tmp/{language}.md"

    monkeypatch.setattr(run_daily_report.auto_generate_ai, "save_report", fake_save)

    quality_results = {}
    output_path = run_daily_report.generate_and_save_report(
        config={},
        target_date="2026-05-10",
        papers_context="papers-context",
        news_context="news-context",
        language="zh",
        quality_results=quality_results,
    )

    assert output_path == "/tmp/zh.md"
    assert calls == [("2026-05-10", "zh", "clean::fixed::raw-content::papers-context")]
    assert validation_calls == [("clean::fixed::raw-content::papers-context", "2026-05-10", "zh")]
    assert quality_results == {"zh": {"ok": True}}


def test_generate_and_save_report_returns_none_when_generation_fails(monkeypatch):
    monkeypatch.setattr(
        run_daily_report.auto_generate_ai,
        "generate_content",
        lambda config, target_date, papers_context, news_context, language: None,
    )

    output_path = run_daily_report.generate_and_save_report(
        config={},
        target_date="2026-05-10",
        papers_context="papers-context",
        news_context="news-context",
        language="en",
    )

    assert output_path is None
