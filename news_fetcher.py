import datetime
import history_tracker
import json
import os
import rss_news_fetcher

class NewsFetcher:
    def __init__(self, exa_api_key):
        self.api_key = exa_api_key
        self.base_url = "https://api.exa.ai/search"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def _get_domain(self, url):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""

    def fetch_industry_news(self, lookback_days=1, use_domestic=False):
        news = self._fetch_from_exa(lookback_days, use_domestic)

        if not news:
            print(f"Exa API returned no news, falling back to {'domestic' if use_domestic else 'international'} RSS feeds...")
            news = rss_news_fetcher.fetch_rss_news(max_items=10, use_domestic=use_domestic)

        return news

    def _fetch_from_exa(self, lookback_days=1, use_domestic=False):
        try:
            if not self.api_key:
                print("No Exa API key provided. Skipping Exa fetch.")
                return []

            start_date = (datetime.datetime.now() - datetime.timedelta(days=lookback_days)).strftime("%Y-%m-%d") + "T00:00:00.000Z"
            
            queries = [
                "drone UAV remote sensing agriculture precision farming satellite imagery news",
                "GIS urban planning smart city digital twin geospatial analytics news",
                "satellite earth observation environmental monitoring climate change news",
                "Spatial Intelligence GeoAI World Models 3D Generative AI",
                "geospatial AI machine learning computer vision mapping industry",
            ]

            import robust_fetch
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

                print(f"Fetching news from Exa (query: {query[:50]}...)...")
                try:
                    response = robust_fetch.robust_post(self.base_url, headers=self.headers, json=payload, use_domestic=use_domestic, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    all_results.extend(data.get("results", []))
                except Exception as e:
                    print(f"Query failed: {e}")
                    continue

            seen_urls = set()
            unique_results = []
            for item in all_results:
                url = item.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(item)

            valid_news = []
            domain_counts = {}

            for item in unique_results:
                url = item.get("url")
                title = item.get("title")
                published_date = item.get("publishedDate")

                if history_tracker.is_news_in_history(url):
                    print(f"Skipping duplicate news: {title}")
                    continue

                if not title or not url:
                    continue

                domain = self._get_domain(url)
                if domain in domain_counts and domain_counts[domain] >= 2:
                    print(f"Skipping to maintain diversity (domain: {domain}): {title}")
                    continue

                domain_counts[domain] = domain_counts.get(domain, 0) + 1

                highlights = item.get("highlights", [])
                summary = highlights[0] if highlights else item.get("text", "")[:200]
                valid_news.append({
                    "title": title,
                    "url": url,
                    "date": published_date,
                    "summary": summary
                })

            print(f"Fetched {len(valid_news)} diverse news items from Exa.")
            return valid_news

        except Exception as e:
            print(f"Error fetching news from Exa: {e}")
            return []

if __name__ == "__main__":
    key = os.environ.get("EXA_API_KEY", "")
    if key:
        fetcher = NewsFetcher(key)
        news = fetcher.fetch_industry_news()
        print(json.dumps(news, indent=2, ensure_ascii=False))
    else:
        print("Set EXA_API_KEY to test.")
