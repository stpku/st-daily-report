import datetime
import history_db
import json
import os
from urllib.parse import urlparse

import robust_fetch
import rss_news_fetcher
from log import logger


class NewsFetcher:
    def __init__(self, exa_api_key):
        self.api_key = exa_api_key
        self.base_url = "https://api.exa.ai/search"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    @staticmethod
    def _get_domain(url):
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    def fetch_industry_news(self, lookback_days=1, use_domestic=False):
        news = self._fetch_from_exa(lookback_days, use_domestic)

        if not news:
            logger.info("Exa API returned no news, falling back to %s RSS feeds...",
                        'domestic' if use_domestic else 'international')
            news = rss_news_fetcher.fetch_rss_news(max_items=10, use_domestic=use_domestic)

        filtered = self._filter_news(news)
        if len(filtered) < 3 and news:
            logger.info("Too few fresh news items after history filtering; reusing recent candidates.")
            filtered = self._filter_news(news, allow_history=True)
        return filtered

    def _fetch_from_exa(self, lookback_days=1, use_domestic=False):
        try:
            if not self.api_key:
                logger.info("No Exa API key provided. Skipping Exa fetch.")
                return []

            start_date = (datetime.datetime.now() - datetime.timedelta(days=lookback_days)).strftime("%Y-%m-%d") + "T00:00:00.000Z"

            queries = [
                "drone UAV remote sensing agriculture precision farming satellite imagery news",
                "GIS urban planning smart city digital twin geospatial analytics news",
                "satellite earth observation environmental monitoring climate change news",
                "Spatial Intelligence GeoAI World Models 3D Generative AI",
                "geospatial AI machine learning computer vision mapping industry",
            ]

            all_results = []

            for query in queries:
                payload = {
                    "query": query,
                    "numResults": 8,
                    "startPublishedDate": start_date,
                    "useAutoprompt": True,
                    "contents": {
                        "text": True,
                        "highlights": True
                    }
                }

                logger.info("Fetching news from Exa (query: %s...)", query[:50])
                try:
                    response = robust_fetch.robust_post(self.base_url, headers=self.headers, json=payload, use_domestic=use_domestic, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    all_results.extend(data.get("results", []))
                except Exception as e:
                    logger.warning("Query failed: %s", e)
                    continue

            seen_urls = set()
            unique_results = []
            for item in all_results:
                url = item.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(item)

            valid_news = []
            for item in unique_results:
                url = item.get("url")
                title = item.get("title")
                published_date = item.get("publishedDate")
                if not title or not url:
                    continue
                highlights = item.get("highlights", [])
                summary = highlights[0] if highlights else item.get("text", "")[:200]
                valid_news.append({
                    "title": title,
                    "url": url,
                    "date": published_date,
                    "summary": summary
                })

            logger.info("Fetched %d candidate news items from Exa.", len(valid_news))
            return valid_news

        except Exception as e:
            logger.error("Error fetching news from Exa: %s", e)
            return []

    def _filter_news(self, items, max_items=10, allow_history=False):
        filtered = []
        domain_counts = {}
        seen_urls = set()

        for item in items:
            url = item.get("url")
            title = item.get("title")
            if not title or not url or url in seen_urls:
                continue
            seen_urls.add(url)

            if not allow_history and history_db.is_news_in_history(url):
                logger.debug("Skipping duplicate news from history DB: %s", title)
                continue

            domain = self._get_domain(url)
            if domain_counts.get(domain, 0) >= 2:
                logger.debug("Skipping to maintain diversity (domain: %s): %s", domain, title)
                continue

            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            filtered.append(item)
            if len(filtered) >= max_items:
                break

        logger.info("Kept %d news items after history + diversity filtering.", len(filtered))
        return filtered

if __name__ == "__main__":
    key = os.environ.get("EXA_API_KEY", "")
    if key:
        fetcher = NewsFetcher(key)
        news = fetcher.fetch_industry_news()
        print(json.dumps(news, indent=2, ensure_ascii=False))
    else:
        print("Set EXA_API_KEY to test.")
