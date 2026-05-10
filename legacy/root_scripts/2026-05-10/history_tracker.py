import json
import os
import re
import path_utils

HISTORY_FILE = path_utils.resolve_path(
    path_utils.runtime_state_path('history.json'),
    os.path.join(os.path.dirname(__file__), 'history.json'),
)

def load_history():
    default_history = {"projects": [], "papers": [], "news_urls": []}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for key in default_history:
                    if key not in data:
                        data[key] = []
                return data
            except json.JSONDecodeError:
                return default_history
    return default_history

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def normalize_text(text):
    # Remove non-alphanumeric characters and whitespace for comparison
    # Keep only English letters and numbers, remove Chinese and special chars
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower()).strip()

def is_project_in_history(name):
    history = load_history()
    projects = history.get("projects", [])
    
    norm_name = normalize_text(name)
    if not norm_name:
        return False
        
    for p in projects:
        norm_p = normalize_text(p)
        if not norm_p:
            continue
            
        if norm_name == norm_p:
            return True
            
        # Substring matching for longer names (avoid short acronyms triggering false positives)
        if len(norm_name) > 4 and len(norm_p) > 4:
            if norm_name in norm_p or norm_p in norm_name:
                return True
                
    return False

def is_news_in_history(url):
    history = load_history()
    return url in history.get("news_urls", [])

def is_paper_in_history(title):
    history = load_history()
    papers = history.get("papers", [])
    
    norm_title = normalize_text(title)
    if not norm_title:
        return False
        
    for p in papers:
        # p can be just title or a dict, assume title string for now based on existing usage
        p_title = p if isinstance(p, str) else p.get('title', '')
        if normalize_text(p_title) == norm_title:
            return True
            
    return False

def add_project(name):
    history = load_history()
    if not is_project_in_history(name):
        history.setdefault("projects", []).append(name)
        save_history(history)
        return True
    return False

def add_news_url(url):
    history = load_history()
    if url not in history.get("news_urls", []):
        history.setdefault("news_urls", []).append(url)
        save_history(history)
        return True
    return False

def add_paper(title):
    history = load_history()
    if not is_paper_in_history(title):
        history.setdefault("papers", []).append(title)
        save_history(history)
        return True
    return False

def get_recent_projects(limit=20):
    history = load_history()
    projects = history.get("projects", [])
    return projects

def update_history_from_content(content):
    """
    Parses the generated Markdown content to find Open Source Projects, Papers, and News URLs, then updates history.
    """
    history = load_history()

    # --- Papers ---
    paper_section_match = re.search(r'(## A\.|## Section A：).*Top Papers.*?(?=## B\.|## Section B：|$)', content, re.DOTALL)
    new_papers = []
    if paper_section_match:
        section_text = paper_section_match.group(0)
        # Extract paper titles and links
        # Pattern: N) **Chinese Title**（*English Title*）
        paper_items = re.findall(r'^\d+\)\s+\*\*(.*?)\*\*（\*(.*?)\*）', section_text, re.MULTILINE)

        for chinese_title, english_title in paper_items:
            paper_title = f"{chinese_title.strip()}（{english_title.strip()}）"
            if paper_title and not is_paper_in_history(paper_title):
                add_paper(paper_title)
                new_papers.append(paper_title)

    if new_papers:
        print(f"Updated history with {len(new_papers)} new papers.")

    # --- Projects ---
    project_section_match = re.search(r'(## C\.|## Section C：).*Open Source Projects.*?(?=## D\.|## 3 New Ideas|$)', content, re.DOTALL)
    new_projects = []
    if project_section_match:
        section_text = project_section_match.group(0)
        project_names = re.findall(r'\*\*(.*?)\*\*', section_text)

        for name in project_names:
            name = name.strip()
            if len(name) > 2 and not is_project_in_history(name):
                add_project(name)
                new_projects.append(name)

    if new_projects:
        print(f"Updated history with new projects: {new_projects}")

    # --- News URLs ---
    news_section_match = re.search(r'(## B\.|## Section B：).*Industry News.*?(?=## C\.|## Section C：|## 3 New Ideas|$)', content, re.DOTALL)
    new_urls = []
    if news_section_match:
        section_text = news_section_match.group(0)
        # Find all http/https links
        urls = re.findall(r'(https?://[^\s\)]+)', section_text)

        for url in urls:
            url = url.strip().rstrip(')') # cleanup markdown link closing paren
            if not is_news_in_history(url):
                add_news_url(url)
                new_urls.append(url)

    if new_urls:
        print(f"Updated history with {len(new_urls)} new news URLs.")

    return new_projects
