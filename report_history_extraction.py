from __future__ import annotations

import re
from typing import List


def find_section(content: str, start_pattern: str, end_pattern: str) -> str:
    match = re.search(
        rf"{start_pattern}.*?(?={end_pattern}|$)",
        content,
        re.DOTALL,
    )
    return match.group(0) if match else ""


def extract_paper_titles(section_text: str) -> List[str]:
    titles: List[str] = []
    paper_items = re.findall(
        r"^\d+\)\s+\*\*(.*?)\*\*[（(](.+?)[）)]",
        section_text,
        re.MULTILINE,
    )
    for chinese_title, english_title in paper_items:
        paper_title = f"{chinese_title.strip()}（{english_title.strip()}）"
        if paper_title:
            titles.append(paper_title)
    return titles


def extract_project_names(section_text: str) -> List[str]:
    names: List[str] = []
    for name in re.findall(r"\*\*(.*?)\*\*", section_text):
        clean_name = name.strip()
        if len(clean_name) > 2:
            names.append(clean_name)
    return names


def extract_news_urls(section_text: str) -> List[str]:
    return [
        url.strip().rstrip(")")
        for url in re.findall(r"(https?://[^\s\)]+)", section_text)
    ]
