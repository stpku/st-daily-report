import datetime
import xml.etree.ElementTree as ET
from typing import List, Tuple

from log import logger
from robust_fetch import robust_get


RSS_FEEDS_INTERNATIONAL: List[Tuple[str, float]] = [
    # ("https://deepmind.google/blog/feed.xml", 0.9),  # 404
    # ("https://openai.com/blog/rss.xml", 0.9),  # brotli decode error
    # ("https://research.google/blog/feed.xml", 0.9),  # hangs
    ("https://www.esri.com/arcgis-blog/feed", 0.7),
    ("https://blogs.nvidia.com/feed", 0.8),
    ("https://research.ibm.com/blog/feed", 0.8),
    ("https://www.mdpi.com/rss/journal/remotesensing", 0.6),
    ("https://www.earthdata.nasa.gov/learn/feed", 0.7),
    ("https://www.nasa.gov/rss/dyn/lg.rss", 0.7),
]

RSS_FEEDS_DOMESTIC: List[Tuple[str, float]] = [
    ("https://36kr.com/feed", 0.85),
    ("https://www.jiqizhixin.com/rss", 0.8),
    ("https://m.zhidx.com/rss", 0.75),
    ("https://cn.technode.com/feed", 0.7),
]

KEYWORDS_HIGH = [
    "world model", "world-model", "geospatial", "geoai", "spatial intelligence",
    "remote sensing", "earth observation", "3d", "embodied ai", "robotics",
    "foundation model", "satellite", "lidar", "spatial reasoning",
    # CN
    "大模型", "具身智能", "多模态", "视觉大模型", "生成式ai", "通用人工智能", "智能体",
    "自动驾驶", "人形机器人", "人工智能", "计算机视觉", "遥感",
]

KEYWORDS_MEDIUM = [
    "machine learning", "deep learning", "neural network", "computer vision", "ai model",
    # CN
    "机器学习", "深度学习", "神经网络",
]


def _score_news(item: dict, source_authority: float) -> float:
    title = (item.get("title") or "").lower()
    summary = (item.get("summary") or "").lower()
    text = f"{title} {summary}"

    high = sum(1 for kw in KEYWORDS_HIGH if kw in text)
    med = sum(1 for kw in KEYWORDS_MEDIUM if kw in text)
    if high > 0:
        kw_score = min(high, 3) / 3.0
    elif med > 0:
        kw_score = 0.5 * min(med, 2) / 2.0
    else:
        kw_score = 0.0

    # Hard gate: zero keyword hits → score 0 regardless of recency/authority.
    # Prevents weakly-related items (e.g., GeForce NOW, general tech news) from
    # entering the candidate pool on recency alone.
    if high == 0 and med == 0:
        return 0.0

    recency = 0.5
    dstr = item.get("date") or ""
    try:
        if "T" in dstr:
            dt = datetime.datetime.fromisoformat(dstr.replace("Z", "+00:00"))
        else:
            dt = datetime.datetime.strptime(dstr[:10], "%Y-%m-%d")
        days = (datetime.datetime.now() - dt).days
        recency = max(0.0, 1.0 - days / 7.0)
    except Exception:
        recency = 0.5

    return min(kw_score * 0.5 + recency * 0.3 + source_authority * 0.2, 1.0)


def fetch_rss_news(max_items: int = 10, use_domestic: bool = False) -> List[dict]:
    # Always fetch from both domestic and international sources
    # The use_domestic parameter only affects network routing in robust_get
    feeds = RSS_FEEDS_INTERNATIONAL + RSS_FEEDS_DOMESTIC
    all_items: List[dict] = []
    for url, authority in feeds:
        try:
            logger.info("Fetching RSS feed: %s", url)
            resp = robust_get(url, timeout=10)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            for item in root.findall('.//item'):
                title_el = item.find('title')
                link_el = item.find('link')
                date_el = item.find('pubDate')
                if title_el is None or link_el is None or not title_el.text or not link_el.text:
                    continue
                date_str = (date_el.text or "")[:10] if date_el is not None else datetime.datetime.now().strftime("%Y-%m-%d")
                news = {
                    "title": title_el.text.strip(),
                    "url": link_el.text.strip(),
                    "date": date_str,
                    "summary": (title_el.text or "").strip()[:200],
                }
                news["importance_score"] = _score_news(news, authority)
                all_items.append(news)
                if len(all_items) >= max_items * 2:
                    logger.debug("Collected %d items, stopping feed fetch", len(all_items))
                    break
        except Exception as e:
            logger.warning("Failed to fetch RSS feed %s: %s", url, e)
            continue

    all_items.sort(key=lambda x: x.get("importance_score", 0.0), reverse=True)
    return all_items[:max_items]
