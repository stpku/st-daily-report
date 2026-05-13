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
        "## A) Top Papers（精选 3-5 篇）\n"
        "1) **中文标题**（English Title）\n"
        "\n"
        "## B) Industry News（产业动态，精选 3-5 条）\n"
        "1) **News Item**\n"
        "   - 来源：https://example.com/news-item\n"
        "\n"
        "## C) Tools / Data / Open Source Updates\n"
        "1) **Project Alpha**\n"
        "   - 项目地址：https://example.com/project-alpha\n"
        "\n"
        "## D) Problem Leads / Innovation Opportunities\n"
        "1) **Opportunity One**\n"
    )

    result = history_db.update_history_from_content(content)

    assert "Project Alpha" in result["new_project_names"]
    assert result["parsed_papers"] >= 1
    assert result["parsed_news"] >= 1
    assert result["parsed_projects"] >= 1
    assert history_db.is_paper_in_history("中文标题（English Title）") is True
    assert history_db.is_project_in_history("Project Alpha") is True
    assert history_db.is_news_in_history("https://example.com/news-item") is True


def test_update_history_from_content_matches_actual_daily_report_format(monkeypatch, tmp_path):
    """Regression test: history extraction works with real ## A) format."""
    _use_temp_db(monkeypatch, tmp_path)
    content = (
        "## A) Top Papers（精选 3-5 篇）\n"
        "\n"
        "1) **测试论文**（Test Paper）\n"
        "   - 原文：http://arxiv.org/abs/2605.01234v1\n"
        "   - 为什么重要：测试\n"
        "\n"
        "---\n"
        "\n"
        "## B) Industry News（产业动态，精选 3-5 条）\n"
        "\n"
        "1) **测试新闻**\n"
        "   - 来源：https://example.com/news-test\n"
        "   - 影响：测试\n"
        "\n"
        "---\n"
        "\n"
        "## C) Tools / Data / Open Source Updates\n"
        "\n"
        "1) **TestProject**\n"
        "   - 项目地址：https://github.com/test/testproject\n"
        "\n"
        "---\n"
        "\n"
        "## D) Problem Leads / Innovation Opportunities\n"
        "\n"
        "1) **测试机会**\n"
        "   - 机会：测试\n"
    )
    result = history_db.update_history_from_content(content)
    assert result["parsed_papers"] >= 1
    assert result["parsed_news"] >= 1
    assert result["parsed_projects"] >= 1
    assert history_db.is_paper_in_history("测试论文（Test Paper）") is True
    assert history_db.is_project_in_history("TestProject") is True
    assert history_db.is_news_in_history("https://example.com/news-test") is True


def test_update_history_from_content_returns_structured_counts(monkeypatch, tmp_path):
    """update_history_from_content returns dict with papers/news/projects counts."""
    _use_temp_db(monkeypatch, tmp_path)
    content = (
        "## A) Top Papers\n"
        "1) **Paper1**（English1）\n"
        "2) **Paper2**（English2）\n"
        "\n"
        "## B) Industry News\n"
        "1) **News1**\n"
        "   - Source: https://example.com/1\n"
        "   - Source: https://example.com/2\n"
        "\n"
        "## C) Open Source\n"
        "1) **Proj1**\n"
        "\n"
        "## D) Problem Leads\n"
    )
    result = history_db.update_history_from_content(content)
    assert isinstance(result, dict)
    assert result["parsed_papers"] == 2
    assert result["parsed_news"] == 2
    assert result["parsed_projects"] == 1
    assert result["new_papers"] == 2
    assert result["new_news"] == 2
    assert result["new_projects"] == 1
    assert "Proj1" in result["new_project_names"]


def test_update_history_from_content_matches_chinese_section_titles(monkeypatch, tmp_path):
    """Regression test: history extraction works with Chinese section C/D titles."""
    _use_temp_db(monkeypatch, tmp_path)
    content = (
        "## A) Top Papers（精选 3-5 篇）\n"
        "1) **中文论文**（Chinese Paper）\n"
        "\n"
        "## B) 产业动态（精选 3-5 条）\n"
        "1) **中文新闻**\n"
        "   - 来源：https://example.com/cn-news\n"
        "\n"
        "## C) 工具 / 数据 / 开源更新\n"
        "1) **中文项目**\n"
        "   - 项目地址：https://github.com/test/cn-project\n"
        "\n"
        "## D) 问题线索 / 创新机会\n"
        "1) **中文机会**\n"
    )
    result = history_db.update_history_from_content(content)
    assert "中文项目" in result["new_project_names"]
    assert history_db.is_paper_in_history("中文论文（Chinese Paper）") is True
    assert history_db.is_project_in_history("中文项目") is True
    assert history_db.is_news_in_history("https://example.com/cn-news") is True


def test_init_db_migrates_old_schema_missing_norm_columns(monkeypatch, tmp_path):
    """Regression test: init_db can migrate old database missing title_norm/name_norm columns."""
    import sqlite3

    db_path = tmp_path / "history.db"
    monkeypatch.setattr(history_db, "DB_PATH", str(db_path))

    # Manually create old schema tables (pre-2026-05-13)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute('''
        CREATE TABLE papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            arxiv_id TEXT,
            url TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            url TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE news_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Insert some old data
    conn.execute("INSERT INTO papers (title, arxiv_id) VALUES (?, ?)", ("Old Paper", "2605.99999"))
    conn.execute("INSERT INTO projects (name) VALUES (?)", ("Old Project",))
    conn.execute("INSERT INTO news_urls (url) VALUES (?)", ("https://example.com/old-news",))
    conn.commit()
    conn.close()

    # Run init_db to migrate
    history_db.init_db()

    # Verify columns were added
    conn = sqlite3.connect(str(db_path))
    papers_cols = {c[1] for c in conn.execute("PRAGMA table_info(papers)")}
    projects_cols = {c[1] for c in conn.execute("PRAGMA table_info(projects)")}
    conn.close()

    assert "title_norm" in papers_cols, "papers table should have title_norm column after migration"
    assert "name_norm" in projects_cols, "projects table should have name_norm column after migration"

    # Verify old data was backfilled
    assert history_db.is_paper_in_history("Old Paper") is True
    assert history_db.is_project_in_history("Old Project") is True
    assert history_db.is_news_in_history("https://example.com/old-news") is True

    # Verify new inserts work with normalized matching
    assert history_db.add_paper("Old Paper") is False  # Already exists via normalized match
    assert history_db.add_project("Old Project") is False  # Already exists
