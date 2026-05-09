import xml.etree.ElementTree as ET
from typing import List

from robust_fetch import robust_get


MIRRORS: List[str] = [
    "https://export.arxiv.org",  # Canonical API host
    "http://xxx.itp.ac.cn",      # CAS mirror (CN)
    "https://arxiv.mirrors.cn",  # Alternative CN mirror
]


def _pick_mirror() -> str:
    for base in MIRRORS:
        try:
            # quick HEAD/GET to base (low-cost)
            resp = robust_get(base, timeout=5)
            if resp.status_code < 500:
                return base
        except Exception:
            continue
    return MIRRORS[0]


def fetch_arxiv_papers(query: str = 'all:"GeoAI" OR all:"Remote Sensing" OR all:"World Model" OR all:"Spatio-Temporal"',
                       max_results: int = 10) -> str:
    base = _pick_mirror()
    # Some mirrors expose API under /api/query; export.arxiv.org uses same path
    api = f"{base}/api/query"
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    try:
        resp = robust_get(api, params=params, timeout=60)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        items: List[str] = []
        for entry in root.findall('atom:entry', ns):
            title = (entry.find('atom:title', ns).text or '').strip().replace('\n', ' ')
            summary = (entry.find('atom:summary', ns).text or '').strip().replace('\n', ' ')
            link = (entry.find('atom:id', ns).text or '').strip()
            published = (entry.find('atom:published', ns).text or '')[:10]
            if not title or not link:
                continue
            items.append(f"- Title: {title}\n  Published: {published}\n  Link: {link}\n  Summary: {summary[:200]}...")
        return "\n\n".join(items)
    except Exception:
        return "No papers fetched (Error accessing Arxiv)."
