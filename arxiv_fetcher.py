import xml.etree.ElementTree as ET
import datetime
import re
from typing import List, Set

from robust_fetch import robust_get
import history_db
from log import logger


MIRRORS: List[str] = [
    "https://export.arxiv.org",  # Canonical API host
    "http://xxx.itp.ac.cn",      # CAS mirror (CN)
    "https://arxiv.mirrors.cn",  # Alternative CN mirror
]

_NORM_RE = re.compile(r'[^a-zA-Z0-9]')


def _normalize(text: str) -> str:
    return _NORM_RE.sub('', text.lower()).strip()


def _load_existing_paper_norms() -> Set[str]:
    """Batch-load all normalised paper titles from history into a set.

    This avoids opening a DB connection for every candidate paper inside
    the fetch loop.
    """
    titles = history_db.get_recent_papers_titles(limit=0)
    return {_normalize(t) for t in titles if _normalize(t)}


def _pick_mirror() -> str:
    for base in MIRRORS:
        try:
            resp = robust_get(base, timeout=5)
            if resp.status_code < 500:
                return base
        except Exception:
            continue
    return MIRRORS[0]


def _restore_openalex_abstract(index: dict) -> str:
    if not index:
        return ""
    words = []
    for word, positions in index.items():
        for pos in positions:
            words.append((pos, word))
    return " ".join(word for _, word in sorted(words))


def _fetch_openalex_papers(query: str, max_results: int, candidate_pool: int,
                           known_norms: Set[str]) -> str:
    """Fallback when arXiv API is rate-limited or unavailable."""
    today = datetime.date.today()
    from_date = (today - datetime.timedelta(days=45)).isoformat()
    # Derive a search term from the caller's query as the first candidate
    # Strip arXiv query operators (OR, AND, quotes, field prefixes)
    import re as _re
    cleaned = _re.sub(r'(all:|ti:|au:|abs:|cat:)', '', query)
    cleaned = _re.sub(r'"+', ' ', cleaned)
    cleaned = _re.sub(r'\b(OR|AND)\b', ' ', cleaned)
    cleaned = _re.sub(r'[^\w\s]', ' ', cleaned)
    cleaned = ' '.join(w for w in cleaned.split() if len(w) > 2)[:120]
    queries = []
    if cleaned:
        queries.append(cleaned)
    queries.extend([
        "GeoAI disaster mapping remote sensing",
        "remote sensing artificial intelligence satellite imagery",
        "earth observation foundation model remote sensing",
        "world model weather forecasting earth system",
        "spatiotemporal machine learning geospatial",
    ])
    domain_terms = (
        "geoai", "geospatial", "remote sensing", "satellite", "earth observation",
        "spatial", "spatio-temporal", "spatiotemporal", "world model", "weather",
        "climate", "lidar", "point cloud", "gis", "urban", "mapping", "disaster",
        "agriculture", "hyperspectral", "sar", "segmentation",
    )

    works = []
    seen_ids = set()
    for fallback_query in queries:
        params = {
            "search": fallback_query,
            "filter": f"from_publication_date:{from_date}",
            "sort": "publication_date:desc",
            "per-page": max(max_results, candidate_pool),
            "mailto": "st-dailyreport@example.com",
        }
        try:
            resp = robust_get("https://api.openalex.org/works", params=params, timeout=45)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("OpenAlex fallback failed (%s): %s", fallback_query, exc)
            continue

        for work in data.get("results", []):
            work_id = work.get("id")
            if work_id and work_id in seen_ids:
                continue
            if work_id:
                seen_ids.add(work_id)
            works.append(work)

    items: List[str] = []
    skipped_duplicates = 0
    for work in works:
        title = (work.get("display_name") or "").strip()
        if not title:
            continue
        norm = _normalize(title)
        if norm and norm in known_norms:
            skipped_duplicates += 1
            continue
        abstract = _restore_openalex_abstract(work.get("abstract_inverted_index") or {})
        haystack = f"{title} {abstract}".lower()
        relevance = sum(1 for term in domain_terms if term in haystack)
        if relevance < 2:
            continue

        publication_date = work.get("publication_date") or ""
        primary = work.get("primary_location") or {}
        landing_page = primary.get("landing_page_url")
        doi = work.get("doi")
        link = landing_page or doi or work.get("id")
        source = ((primary.get("source") or {}).get("display_name") or "OpenAlex").strip()
        if not link or not abstract:
            continue

        items.append(
            f"- Title: {title}\n"
            f"  Published: {publication_date}\n"
            f"  Source: {source}\n"
            f"  Link: {link}\n"
            f"  Summary: {abstract[:200]}..."
        )
        if len(items) >= max_results:
            break

    if skipped_duplicates:
        logger.info("Skipped %d recent OpenAlex papers already in history.", skipped_duplicates)
    if items:
        logger.info("Using OpenAlex fallback with %d academic papers.", len(items))
    return "\n\n".join(items)


def fetch_arxiv_papers(query: str = 'all:"GeoAI" OR all:"Remote Sensing" OR all:"World Model" OR all:"Spatio-Temporal"',
                       max_results: int = 10,
                       candidate_pool: int = 30) -> str:
    # Batch-load known paper titles once
    known_norms = _load_existing_paper_norms()

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max(max_results, candidate_pool),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    first_base = _pick_mirror()
    bases = [first_base] + [base for base in MIRRORS if base != first_base]
    last_error = None

    for base in bases:
        api = f"{base}/api/query"
        try:
            resp = robust_get(api, params=params, timeout=60)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            items: List[str] = []
            skipped_duplicates = 0
            for entry in root.findall('atom:entry', ns):
                title = (entry.find('atom:title', ns).text or '').strip().replace('\n', ' ')
                summary = (entry.find('atom:summary', ns).text or '').strip().replace('\n', ' ')
                link = (entry.find('atom:id', ns).text or '').strip()
                published = (entry.find('atom:published', ns).text or '')[:10]
                if not title or not link:
                    continue
                norm = _normalize(title)
                if norm and norm in known_norms:
                    skipped_duplicates += 1
                    continue
                items.append(f"- Title: {title}\n  Published: {published}\n  Link: {link}\n  Summary: {summary[:200]}...")
                if len(items) >= max_results:
                    break
            if skipped_duplicates:
                logger.info("Skipped %d recent papers already in history.", skipped_duplicates)
            if items:
                return "\n\n".join(items)
            logger.info("No fresh arXiv papers from %s; trying next mirror.", base)
        except Exception as exc:
            last_error = exc
            logger.warning("arXiv mirror failed (%s): %s", base, exc)
            continue

    logger.error("No papers fetched from arXiv mirrors. Last error: %s", last_error)
    return _fetch_openalex_papers(query, max_results=max_results,
                                  candidate_pool=candidate_pool, known_norms=known_norms)
