import json
from pathlib import Path

import history_db


def _use_temp_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "history.db"
    monkeypatch.setattr(history_db, "DB_PATH", str(db_path))
    history_db.init_db()
    return db_path


def test_add_news_url_deduplicates_exact_match(monkeypatch, tmp_path):
    _use_temp_db(monkeypatch, tmp_path)

    assert history_db.add_news_url("https://example.com/news/1") is True
    assert history_db.is_news_in_history("https://example.com/news/1") is True
    assert history_db.add_news_url("https://example.com/news/1") is False
    assert history_db.get_recent_news_urls() == ["https://example.com/news/1"]


def test_project_history_uses_normalized_name_matching(monkeypatch, tmp_path):
    _use_temp_db(monkeypatch, tmp_path)

    assert history_db.add_project("World Model Lab") is True
    assert history_db.is_project_in_history("world-model lab") is True
    assert history_db.add_project("world-model lab") is False


def test_get_recent_papers_preserves_metadata(monkeypatch, tmp_path):
    _use_temp_db(monkeypatch, tmp_path)

    assert history_db.add_paper(
        "GeoAI for Flood Mapping",
        arxiv_id="2605.12345",
        url="https://arxiv.org/abs/2605.12345",
    ) is True

    papers = history_db.get_recent_papers(limit=5)
    assert len(papers) == 1
    assert papers[0]["title"] == "GeoAI for Flood Mapping"
    assert papers[0]["arxiv_id"] == "2605.12345"
    assert papers[0]["url"] == "https://arxiv.org/abs/2605.12345"
    assert papers[0]["added_at"]


def test_migrate_from_json_loads_all_supported_item_types(monkeypatch, tmp_path):
    _use_temp_db(monkeypatch, tmp_path)
    json_path = tmp_path / "history.json"
    json_path.write_text(
        json.dumps(
            {
                "papers": ["Paper A"],
                "projects": ["Project A"],
                "news_urls": ["https://example.com/news/migrated"],
            }
        ),
        encoding="utf-8",
    )

    history_db.migrate_from_json(str(json_path))

    assert history_db.is_paper_in_history("Paper A") is True
    assert history_db.is_project_in_history("Project A") is True
    assert history_db.is_news_in_history("https://example.com/news/migrated") is True


def test_extract_paper_titles_handles_plain_english_title_parentheses():
    section = (
        "## A. Top Papers\n"
        "1) **中文标题**（English Title Without Markdown）\n"
        "2) **另一个标题**(Another English Title)\n"
    )

    titles = history_db._extract_paper_titles(section)

    assert titles == [
        "中文标题（English Title Without Markdown）",
        "另一个标题（Another English Title）",
    ]


def test_update_history_from_content_supports_new_section_names(monkeypatch, tmp_path):
    _use_temp_db(monkeypatch, tmp_path)
    content = (
        "## A. Top Papers\n"
        "1) **中文标题**（English Title）\n"
        "\n"
        "## B. Industry News\n"
        "1) **News Item**\n"
        "   - 来源：https://example.com/news-item\n"
        "\n"
        "## C. Tools / Data / Open Source Updates\n"
        "1) **Project Alpha**\n"
        "   - 项目地址：https://example.com/project-alpha\n"
        "\n"
        "## D. Problem Leads / Innovation Opportunities\n"
        "1) **Opportunity One**\n"
    )

    new_projects = history_db.update_history_from_content(content)

    assert "Project Alpha" in new_projects
    assert history_db.is_paper_in_history("中文标题（English Title）") is True
    assert history_db.is_project_in_history("Project Alpha") is True
    assert history_db.is_news_in_history("https://example.com/news-item") is True
