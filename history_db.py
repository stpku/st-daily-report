import sqlite3
import os
import re
from contextlib import contextmanager
from typing import List, Optional
from datetime import datetime
import path_utils
from log import logger
from report_history_extraction import (
    extract_news_urls as _extract_news_urls,
    extract_paper_titles as _extract_paper_titles,
    extract_project_names as _extract_project_names,
    find_section as _find_section,
)


DB_PATH = path_utils.resolve_path(
    path_utils.runtime_state_path('history.db'),
    os.path.join(os.path.dirname(__file__), 'history.db'),
)

_NORM_RE = re.compile(r'[^a-zA-Z0-9]')


def _normalize(text: str) -> str:
    return _NORM_RE.sub('', text.lower()).strip()


@contextmanager
def _get_connection():
    """Provide a transactional SQLite connection with auto-commit/close."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                title_norm TEXT,
                arxiv_id TEXT,
                url TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_title_norm ON papers(title_norm)')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                name_norm TEXT,
                url TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_name_norm ON projects(name_norm)')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_urls_url ON news_urls(url)')

        # Backfill norm columns for existing rows
        cursor.execute("SELECT id, title FROM papers WHERE title_norm IS NULL")
        for row_id, title in cursor.fetchall():
            cursor.execute("UPDATE papers SET title_norm = ? WHERE id = ?", (_normalize(title), row_id))
        cursor.execute("SELECT id, name FROM projects WHERE name_norm IS NULL")
        for row_id, name in cursor.fetchall():
            cursor.execute("UPDATE projects SET name_norm = ? WHERE id = ?", (_normalize(name), row_id))


def is_paper_in_history(title: str) -> bool:
    norm_title = _normalize(title)
    if not norm_title:
        return False

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT 1 FROM papers WHERE title_norm = ? LIMIT 1',
            (norm_title,),
        )
        return cursor.fetchone() is not None


def is_project_in_history(name: str) -> bool:
    norm_name = _normalize(name)
    if not norm_name:
        return False

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT name_norm FROM projects WHERE name_norm = ? LIMIT 1',
            (norm_name,),
        )
        if cursor.fetchone():
            return True

        # Substring matching for longer names
        if len(norm_name) > 4:
            cursor.execute(
                "SELECT name_norm FROM projects WHERE name_norm LIKE ? LIMIT 1",
                (f"%{norm_name}%",),
            )
            if cursor.fetchone():
                return True
            cursor.execute(
                "SELECT name_norm FROM projects WHERE ? LIKE '%' || name_norm || '%' LIMIT 1",
                (norm_name,),
            )
            if cursor.fetchone():
                return True

    return False


def add_paper(title: str, arxiv_id: Optional[str] = None, url: Optional[str] = None) -> bool:
    if is_paper_in_history(title):
        return False

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO papers (title, title_norm, arxiv_id, url)
            VALUES (?, ?, ?, ?)
        ''', (title, _normalize(title), arxiv_id, url))
    return True


def update_paper_timestamp(title: str) -> bool:
    """Update the added_at timestamp for an existing paper."""
    if not is_paper_in_history(title):
        return False

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE papers SET added_at = CURRENT_TIMESTAMP WHERE title_norm = ?
        ''', (_normalize(title),))
    return True


def add_project(name: str, url: Optional[str] = None) -> bool:
    if is_project_in_history(name):
        return False

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, name_norm, url)
            VALUES (?, ?, ?)
        ''', (name, _normalize(name), url))
    return True


def update_project_timestamp(name: str) -> bool:
    """Update the added_at timestamp for an existing project."""
    if not is_project_in_history(name):
        return False

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE projects SET added_at = CURRENT_TIMESTAMP WHERE name_norm = ?
        ''', (_normalize(name),))
    return True


def add_news_url(url: str) -> bool:
    if is_news_in_history(url):
        return False

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO news_urls (url)
            VALUES (?)
        ''', (url,))
    return True


def get_recent_projects(limit: int = 20) -> List[str]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        if limit <= 0:
            cursor.execute('SELECT name FROM projects ORDER BY added_at DESC')
        else:
            cursor.execute('SELECT name FROM projects ORDER BY added_at DESC LIMIT ?', (limit,))
        projects = [row[0] for row in cursor.fetchall()]
    return projects


def get_recent_papers(limit: int = 10) -> List[dict]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        if limit <= 0:
            cursor.execute('SELECT title, arxiv_id, url, added_at FROM papers ORDER BY added_at DESC')
        else:
            cursor.execute('SELECT title, arxiv_id, url, added_at FROM papers ORDER BY added_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()

    papers = []
    for row in rows:
        papers.append({
            'title': row[0],
            'arxiv_id': row[1],
            'url': row[2],
            'added_at': row[3]
        })
    return papers


def get_recent_news_urls(limit: int = 20) -> List[str]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        if limit <= 0:
            cursor.execute('SELECT url FROM news_urls ORDER BY added_at DESC')
        else:
            cursor.execute('SELECT url FROM news_urls ORDER BY added_at DESC LIMIT ?', (limit,))
        urls = [row[0] for row in cursor.fetchall()]
    return urls


def is_news_in_history(url: str) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM news_urls WHERE url = ? LIMIT 1', (url,))
        exists = cursor.fetchone() is not None
    return exists


def get_recent_papers_titles(limit: int = 10) -> List[str]:
    """Get recent paper titles as a list of strings."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        if limit <= 0:
            cursor.execute('SELECT title FROM papers ORDER BY added_at DESC')
        else:
            cursor.execute('SELECT title FROM papers ORDER BY added_at DESC LIMIT ?', (limit,))
        papers = [row[0] for row in cursor.fetchall()]
    return papers

def update_history_from_content(content: str) -> List[str]:
    """
    Parse generated Markdown content to extract papers, projects, and news URLs,
    then update history database.
    Returns list of new projects added.
    """
    new_projects = []

    # Papers
    paper_section_text = _find_section(
        content,
        r'(## A\.|## Section A).*Top Papers',
        r'## B\.|## Section B',
    )
    new_papers = []
    for paper_title in _extract_paper_titles(paper_section_text):
        if not is_paper_in_history(paper_title):
            add_paper(paper_title)
            new_papers.append(paper_title)
        else:
            update_paper_timestamp(paper_title)

    if new_papers:
        logger.info("Updated history with %d new papers.", len(new_papers))

    # Projects
    project_section_text = _find_section(
        content,
        r'(## C\.|## Section C).*(Open Source Projects|Tools / Data / Open Source Updates)',
        r'## D\.|## 3 New Ideas|## Problem Leads',
    )
    for name in _extract_project_names(project_section_text):
        if not is_project_in_history(name):
            add_project(name)
            new_projects.append(name)
        else:
            update_project_timestamp(name)

    if new_projects:
        logger.info("Updated history with new projects: %s", new_projects)

    # News URLs
    news_section_text = _find_section(
        content,
        r'(## B\.|## Section B).*Industry News',
        r'## C\.|## Section C|## 3 New Ideas|## Problem Leads',
    )
    new_urls = []
    for url in _extract_news_urls(news_section_text):
        if not is_news_in_history(url):
            add_news_url(url)
            new_urls.append(url)

    if new_urls:
        logger.info("Updated history with %d new news URLs.", len(new_urls))

    return new_projects


def migrate_from_json(json_path: str | None = None):
    if json_path is None:
        json_path = path_utils.resolve_path(
            path_utils.runtime_state_path('history.json'),
            os.path.join(os.path.dirname(__file__), 'history.json'),
        )
    import json

    if not os.path.exists(json_path):
        logger.info("JSON file not found: %s", json_path)
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    migrated_count = 0

    for paper in data.get('papers', []):
        if add_paper(paper):
            migrated_count += 1

    for project in data.get('projects', []):
        if add_project(project):
            migrated_count += 1

    for url in data.get('news_urls', []):
        if add_news_url(url):
            migrated_count += 1

    logger.info("Migrated %d items from %s to SQLite database", migrated_count, json_path)


if __name__ == '__main__':
    init_db()
    migrate_from_json()
    logger.info("Database initialized successfully.")
