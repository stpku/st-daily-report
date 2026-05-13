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


def validate_and_fix_arxiv_links(content: str, papers_context: str) -> tuple[str, int]:
    """Validate arXiv links in generated content and fix incomplete ones.

    Handles formats used in production output:
      - ``原文：[arxiv.org] | URL``
      - ``原文：https://arxiv.org/abs/...``
      - ``Link: https://arxiv.org/...``

    Incomplete links (e.g., ``原文：[arxiv.org] | https://arxiv.org/`` with no
    paper ID) are matched against arXiv IDs found in the surrounding content
    context. When exactly one candidate is found nearby, the bare URL is
    replaced; otherwise it is counted as unresolved.

    Returns:
        tuple[str, int]: (fixed_content, unresolved_count) where unresolved_count
        is the number of bare arXiv URLs that could not be resolved.
    """
    # Extract complete arXiv links from papers_context
    context_links: dict[str, str] = {}
    context_pattern = r'https?://arxiv\.org/abs/([\d\.]+v?\d*)'
    for match in re.finditer(context_pattern, papers_context, re.IGNORECASE):
        paper_id = match.group(1)
        full_url = match.group(0)
        context_links[paper_id] = full_url

    # Collect all complete arXiv URLs already present in content
    content_complete: dict[str, str] = {}
    for match in re.finditer(context_pattern, content, re.IGNORECASE):
        content_complete[match.group(1)] = match.group(0)

    # Merge: prefer content's own complete URLs, fill gaps from context
    available = {**context_links, **content_complete}

    fixed_count = 0
    warning_count = 0
    original_content = content  # save for context lookups

    def _fix_incomplete_url(match: re.Match) -> str:
        nonlocal fixed_count, warning_count
        prefix = match.group(1)

        if not available:
            warning_count += 1
            return match.group(0)

        # Look at surrounding lines (±500 chars) for nearby arXiv IDs
        match_pos = match.start()
        ctx_start = max(0, match_pos - 500)
        ctx_end = min(len(original_content), match_pos + 200)
        local_context = original_content[ctx_start:ctx_end]

        # Find arXiv IDs in this local context
        local_ids = re.findall(r'(\d{4}\.\d{4,5}(?:v\d+)?)', local_context)

        # Match against available URLs
        matching_urls = []
        seen = set()
        for pid in local_ids:
            if pid in available and pid not in seen:
                matching_urls.append(available[pid])
                seen.add(pid)

        # Case 1: Single global candidate → fix it (unambiguous)
        if len(available) == 1:
            best_url = next(iter(available.values()))
            fixed_count += 1
            return f"{prefix}{best_url}"

        # Case 2: Local context found exactly one match → fix it
        if len(matching_urls) == 1:
            fixed_count += 1
            return f"{prefix}{matching_urls[0]}"

        # Case 3: Multiple global candidates and no single local match → unresolved
        warning_count += 1
        return match.group(0)

    # Match "原文：" or "Link:" followed by an incomplete arXiv URL
    content = re.sub(
        r'(原文[：:]\s*(?:\[arxiv\.org\]\s*\|\s*)?)(https?://arxiv\.org/?(?!\S))(?!\s*abs/)',
        _fix_incomplete_url,
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(
        r'(Link[：:]\s*)(https?://arxiv\.org/?(?!\S))(?!\s*abs/)',
        _fix_incomplete_url,
        content,
        flags=re.IGNORECASE,
    )

    if fixed_count > 0:
        logger.warning("Fixed %d incomplete arXiv links via local context matching", fixed_count)

    return content, warning_count


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
