import sqlite3
import os
from typing import List, Optional
from datetime import datetime
import path_utils


DB_PATH = path_utils.resolve_path(
    path_utils.runtime_state_path('history.db'),
    os.path.join(os.path.dirname(__file__), 'history.db'),
)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            arxiv_id TEXT,
            url TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            url TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def is_paper_in_history(title: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    import re
    norm_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower()).strip()

    cursor.execute('SELECT title FROM papers')
    existing_titles = cursor.fetchall()

    for (existing_title,) in existing_titles:
        norm_existing = re.sub(r'[^a-zA-Z0-9]', '', existing_title.lower()).strip()
        if norm_title == norm_existing:
            conn.close()
            return True

    conn.close()
    return False


def is_project_in_history(name: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    import re
    norm_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower()).strip()

    cursor.execute('SELECT name FROM projects')
    existing_names = cursor.fetchall()

    for (existing_name,) in existing_names:
        norm_existing = re.sub(r'[^a-zA-Z0-9]', '', existing_name.lower()).strip()

        if norm_name == norm_existing:
            conn.close()
            return True

        if len(norm_name) > 4 and len(norm_existing) > 4:
            if norm_name in norm_existing or norm_existing in norm_name:
                conn.close()
                return True

    conn.close()
    return False


def is_news_in_history(url: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT 1 FROM news_urls WHERE url = ?', (url,))
    result = cursor.fetchone()

    conn.close()
    return result is not None


def add_paper(title: str, arxiv_id: Optional[str] = None, url: Optional[str] = None) -> bool:
    if is_paper_in_history(title):
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO papers (title, arxiv_id, url)
        VALUES (?, ?, ?)
    ''', (title, arxiv_id, url))

    conn.commit()
    conn.close()
    return True


def update_paper_timestamp(title: str) -> bool:
    """Update the added_at timestamp for an existing paper."""
    if not is_paper_in_history(title):
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE papers SET added_at = CURRENT_TIMESTAMP WHERE title = ?
    ''', (title,))

    conn.commit()
    conn.close()
    return True


def add_project(name: str, url: Optional[str] = None) -> bool:
    if is_project_in_history(name):
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO projects (name, url)
        VALUES (?, ?)
    ''', (name, url))

    conn.commit()
    conn.close()
    return True


def update_project_timestamp(name: str) -> bool:
    """Update the added_at timestamp for an existing project."""
    if not is_project_in_history(name):
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE projects SET added_at = CURRENT_TIMESTAMP WHERE name = ?
    ''', (name,))

    conn.commit()
    conn.close()
    return True


def add_news_url(url: str) -> bool:
    if is_news_in_history(url):
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO news_urls (url)
        VALUES (?)
    ''', (url,))

    conn.commit()
    conn.close()
    return True


def get_recent_projects(limit: int = 20) -> List[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if limit <= 0:
        cursor.execute('SELECT name FROM projects ORDER BY added_at DESC')
    else:
        cursor.execute('SELECT name FROM projects ORDER BY added_at DESC LIMIT ?', (limit,))

    projects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return projects


def get_recent_papers(limit: int = 10) -> List[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if limit <= 0:
        cursor.execute('SELECT title, arxiv_id, url, added_at FROM papers ORDER BY added_at DESC')
    else:
        cursor.execute('SELECT title, arxiv_id, url, added_at FROM papers ORDER BY added_at DESC LIMIT ?', (limit,))

    papers = []
    for row in cursor.fetchall():
        papers.append({
            'title': row[0],
            'arxiv_id': row[1],
            'url': row[2],
            'added_at': row[3]
        })

    conn.close()
    return papers


def get_recent_news_urls(limit: int = 20) -> List[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if limit <= 0:
        cursor.execute('SELECT url FROM news_urls ORDER BY added_at DESC')
    else:
        cursor.execute('SELECT url FROM news_urls ORDER BY added_at DESC LIMIT ?', (limit,))

    urls = [row[0] for row in cursor.fetchall()]
    conn.close()
    return urls


def get_recent_papers_titles(limit: int = 10) -> List[str]:
    """Get recent paper titles as a list of strings."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if limit <= 0:
        cursor.execute('SELECT title FROM papers ORDER BY added_at DESC')
    else:
        cursor.execute('SELECT title FROM papers ORDER BY added_at DESC LIMIT ?', (limit,))

    papers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return papers


def update_history_from_content(content: str) -> List[str]:
    """
    Parse generated Markdown content to extract papers, projects, and news URLs,
    then update history database.
    Returns list of new projects added.
    """
    import re
    new_projects = []

    # Papers
    paper_section_match = re.search(
        r'(## A\.|## Section A).*Top Papers.*?(?=## B\.|## Section B|$)',
        content, re.DOTALL
    )
    new_papers = []
    if paper_section_match:
        section_text = paper_section_match.group(0)
        paper_items = re.findall(r'^\d+\)\s+\*\*(.*?)\*\*（\*(.*?)\*）', section_text, re.MULTILINE)

        for chinese_title, english_title in paper_items:
            paper_title = f"{chinese_title.strip()}（{english_title.strip()}）"
            if paper_title:
                if not is_paper_in_history(paper_title):
                    add_paper(paper_title)
                    new_papers.append(paper_title)
                else:
                    update_paper_timestamp(paper_title)

    if new_papers:
        print(f"Updated history with {len(new_papers)} new papers.")

    # Projects
    project_section_match = re.search(
        r'(## C\.|## Section C).*Open Source Projects.*?(?=## D\.|## 3 New Ideas|$)',
        content, re.DOTALL
    )
    if project_section_match:
        section_text = project_section_match.group(0)
        project_names = re.findall(r'\*\*(.*?)\*\*', section_text)

        for name in project_names:
            name = name.strip()
            if len(name) > 2:
                if not is_project_in_history(name):
                    add_project(name)
                    new_projects.append(name)
                else:
                    update_project_timestamp(name)

    if new_projects:
        print(f"Updated history with new projects: {new_projects}")

    # News URLs
    news_section_match = re.search(
        r'(## B\.|## Section B).*Industry News.*?(?=## C\.|## Section C|## 3 New Ideas|$)',
        content, re.DOTALL
    )
    new_urls = []
    if news_section_match:
        section_text = news_section_match.group(0)
        urls = re.findall(r'(https?://[^\s\)]+)', section_text)

        for url in urls:
            url = url.strip().rstrip(')')
            if not is_news_in_history(url):
                add_news_url(url)
                new_urls.append(url)

    if new_urls:
        print(f"Updated history with {len(new_urls)} new news URLs.")

    return new_projects


def migrate_from_json(json_path: str | None = None):
    if json_path is None:
        json_path = path_utils.resolve_path(
            path_utils.runtime_state_path('history.json'),
            os.path.join(os.path.dirname(__file__), 'history.json'),
        )
    import json

    if not os.path.exists(json_path):
        print(f"JSON file not found: {json_path}")
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

    print(f"Migrated {migrated_count} items from {json_path} to SQLite database")


if __name__ == '__main__':
    init_db()
    migrate_from_json()
    print("Database initialized successfully.")
