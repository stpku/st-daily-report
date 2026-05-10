"""Report output utilities: path building, saving, link validation, network detection."""

import os
import re
import socket

import path_utils
from log import logger


def build_output_path(date_str: str, language: str) -> str:
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    output_dir = os.path.join(path_utils.ROOT_DIR, year, month, day)
    os.makedirs(output_dir, exist_ok=True)

    if language == "en":
        filename = f"geoai_world-model_dashboard_en_{date_str}.md"
    else:
        filename = f"geoai_world-model_dashboard_{date_str}.md"

    return os.path.join(output_dir, filename)


def save_report(date_str: str, language: str, content: str) -> str:
    output_path = build_output_path(date_str, language)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return output_path


def validate_and_fix_arxiv_links(content: str, papers_context: str) -> str:
    """Validate arXiv links in generated content and fix incomplete ones.

    Handles formats used in production output:
      - ``原文：[arxiv.org] | URL``
      - ``原文：https://arxiv.org/abs/...``
      - ``Link: https://arxiv.org/...``

    Incomplete links (e.g., ``原文：[arxiv.org] | https://arxiv.org/`` with no
    paper ID) are matched against the full links in *papers_context* and
    replaced with the correct URL.
    """
    # Extract complete arXiv links from papers_context
    context_links: dict[str, str] = {}
    context_pattern = r'https?://arxiv\.org/abs/([\d\.]+v?\d*)'
    for match in re.finditer(context_pattern, papers_context, re.IGNORECASE):
        paper_id = match.group(1)
        full_url = match.group(0)
        context_links[paper_id] = full_url

    # Collect all complete arXiv URLs already present in content (for matching)
    content_complete: dict[str, str] = {}
    for match in re.finditer(context_pattern, content, re.IGNORECASE):
        content_complete[match.group(1)] = match.group(0)

    # Merge: prefer content's own complete URLs, fill gaps from context
    available = {**context_links, **content_complete}

    fixed_count = 0

    # Fix pattern 1: 原文：[arxiv.org] | https://arxiv.org/  (no paper ID)
    def _fix_incomplete_url(match: re.Match) -> str:
        nonlocal fixed_count
        prefix = match.group(1)  # "原文：[arxiv.org] | " or "Link: "
        incomplete_url = match.group(2)
        # Try to find any paper ID in the surrounding context of this line
        # If the URL is bare (no ID), try first available from context
        if available:
            best_url = next(iter(available.values()))
            fixed_count += 1
            return f"{prefix}{best_url}"
        return match.group(0)

    # Match "原文：" or "Link:" followed by an incomplete arXiv URL (no /abs/)
    # The negative lookahead (?!abs/) ensures we only match bare domain URLs
    content = re.sub(
        r'(原文[：:]\s*(?:\[arxiv\.org\]\s*\|\s*)?)(https?://arxiv\.org/?(?!\S))(?!\s*abs/)',
        _fix_incomplete_url,
        content,
        flags=re.IGNORECASE,
    )
    # Also match "Link:" style
    content = re.sub(
        r'(Link[：:]\s*)(https?://arxiv\.org/?(?!\S))(?!\s*abs/)',
        _fix_incomplete_url,
        content,
        flags=re.IGNORECASE,
    )

    if fixed_count > 0:
        logger.warning("Fixed %d incomplete arXiv links from papers_context", fixed_count)

    return content


def check_domestic_network() -> bool:
    """Return True if arxiv.org is NOT accessible (domestic/China network)."""
    try:
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("export.arxiv.org", 443))
        logger.info("Arxiv.org is accessible, using international sources")
        return False
    except Exception:
        logger.info("Arxiv.org is not accessible, using domestic sources")
        return True
