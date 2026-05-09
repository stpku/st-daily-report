import os
import json
import datetime
import sys
import history_db
import news_fetcher
import arxiv_fetcher
import robust_fetch
import path_utils

CONFIG_FILE = path_utils.resolve_path(
    path_utils.config_path('config_secret.json'),
    os.path.join(os.path.dirname(__file__), 'config_secret.json'),
)


def load_config():
    """Load configuration from JSON file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file not found at {CONFIG_FILE}")
        print("Please create it with your API keys.")
        sys.exit(1)

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_and_fix_arxiv_links(content: str, papers_context: str) -> str:
    """
    Validate arXiv links in generated content and fix incomplete ones.
    If a link is truncated (e.g., "https://arxiv.org/"), try to recover from papers_context.
    """
    import re
    
    # Extract complete arXiv links from papers_context
    context_links = {}
    context_pattern = r'Link:\s*(https?://arxiv\.org/abs/[\d\.]+v?\d*)'
    for match in re.finditer(context_pattern, papers_context, re.IGNORECASE):
        link = match.group(1)
        # Extract paper ID for matching
        paper_id_match = re.search(r'abs/([\d\.]+v?\d*)', link)
        if paper_id_match:
            paper_id = paper_id_match.group(1)
            context_links[paper_id] = link
    
    # Find incomplete links in content
    incomplete_pattern = r'Link:\s*(https?://arxiv\.org/)(?!abs)'
    
    def replace_incomplete(match):
        # If we have context links, use the first one as fallback
        if context_links:
            # Return a placeholder that will be manually reviewed
            return f"Link: [NEEDS_REVIEW - {list(context_links.values())[0]}]"
        return match.group(0)  # Keep original if no context
    
    fixed_content = re.sub(incomplete_pattern, replace_incomplete, content, flags=re.IGNORECASE)
    
    # Count fixed links
    fixed_count = len(re.findall(r'\[NEEDS_REVIEW', fixed_content))
    if fixed_count > 0:
        print(f"WARNING: Found {fixed_count} incomplete arXiv links marked for review")
    
    return fixed_content


def check_domestic_network():
    try:
        import socket
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("export.arxiv.org", 443))
        print("Arxiv.org is accessible, using international sources")
        return False
    except Exception:
        print("Arxiv.org is not accessible, using domestic sources")
        return True


def generate_content(config, date_str, papers_context, news_context, language="zh"):
    api_providers = config.get("api_providers", [])
    if not api_providers:
        print("Error: No API providers configured")
        return None

    if language == "zh":
        lang_instruction = "Chinese (Simplified)"
        title_format = "# GeoAI & World Model Daily Insight"
        scope_line = "**Scope:** GeoAI（空间智能/遥感/GIS+AI）+ World Model（3D生成与通用模拟/具身智能）"
        priorities_text = "## 今日判断"
        keyword_label = "今日关键词"
        header_example_keywords = "AOD / Sentinel-2 / 物理世界模型 / 可信预测"
    else:
        lang_instruction = "English"
        title_format = "# GeoAI + World Model Compact Dashboard"
        scope_line = "**Scope:** GeoAI (Spatial Intelligence) + World Model (3D Generation & Simulation)"
        priorities_text = "## Today's Read"
        keyword_label = "Keywords"
        header_example_keywords = "AOD / Sentinel-2 / physical world models / calibrated forecasting"

    recent_projects = history_db.get_recent_projects()
    recent_papers = history_db.get_recent_papers_titles()
    history_constraint = ""
    if recent_projects:
        project_list_str = ", ".join(recent_projects)
        history_constraint = f"CRITICAL: Do NOT suggest the following open source projects as they were recently featured: {project_list_str}. Find DIFFERENT relevant projects."

    papers_constraint = ""
    if recent_papers:
        paper_list_str = ", ".join(recent_papers[:10])
        papers_constraint = f"CRITICAL: Do NOT suggest the following papers as they were recently featured: {paper_list_str}. Find DIFFERENT relevant papers."

    system_prompt = f"""Generate a GeoAI Daily Dashboard for date: {date_str}.

**CRITICAL INSTRUCTION - HEADER FORMAT:**
1. First line MUST be the report title in format: # GeoAI & World Model Daily Insight
2. DO NOT place any news titles or content in the header
3. The header should only contain:
   - Line 1: # GeoAI & World Model Daily Insight
   - Line 2: Date: {date_str} (plain text, NO bold markers)
   - Line 3: {priorities_text}
   - Lines 4-6: exactly 3 bullet points, each explaining a concrete trend or judgment
   - Line 7: {keyword_label}: keyword1 / keyword2 / keyword3 / keyword4
4. Lines 9-11: Blank line
5. Lines 12+: News context (for generating content)

**Structure Requirements:**
1. Header: Title only (on first line), Date (plain text), {priorities_text} (3 bullets), {keyword_label} (one short line)
    - Format example:
      # GeoAI & World Model Daily Insight
      Date: {date_str}
      {priorities_text}
      - Point 1...
      - Point 2...
      - Point 3...
      {keyword_label}: {header_example_keywords}
    - IMPORTANT: Do NOT use Scope in the header. Keep the first screen short and scannable on mobile.

2. Section A: Top Papers（精选 3-5 篇）- 3-5 papers with Chinese translation + original English title + 原文 + 为什么重要
   **CRITICAL CONSTRAINT: Top Papers MUST ONLY contain academic papers from peer-reviewed sources: arxiv.org, top-tier conferences (CVPR, ICCV, ECCV, NeurIPS, ICLR, AAAI, IJCAI, SIGGRAPH, IGARSS, ISPRS), or top journals (Nature, Science, IEEE TGRS, Remote Sensing of Environment, ISPRS Journal). DO NOT include blog posts, company announcements, or non-academic news articles.**
   **CRITICAL: You MUST preserve the exact arXiv links from the input papers_context. DO NOT fabricate, truncate, or modify paper links. Each 原文字段 must contain the complete URL (e.g., http://arxiv.org/abs/2604.15086v1), NOT just "https://arxiv.org/".**

3. Section B: Industry News（产业动态，精选 3-5 条）- 3-5 news items with Title + 来源 + 影响
   **CRITICAL CONSTRAINT: Diversify news sources - maximum 2 items from the same company/domain (e.g., max 2 from openai.com). Prioritize application-focused news (agriculture, urban planning, disaster response, environmental monitoring, drone/satellite applications) over pure AI model announcements. Skip weakly related finance/crypto/general market items unless the GeoAI or World Model relevance is direct and concrete.**
4. Section C: Open Source Projects（开源精选）- 4-5 projects with Name + GitHub/项目地址 + 为什么关注. Prefer projects that connect to today's paper/news themes; avoid generic repeat items unless there is a direct reason today.
5. Section D: 3 New Ideas（GeoAI × World Model 灵感 3 则）- 3 ideas with Title + 灵感

**Format Requirements:**
- Use markdown format with proper hierarchy
- Paper format: "N) **Chinese Title**（*English Title*）\\n   - 原文：arXiv | [complete URL]\\n   - 为什么重要：[one-sentence insight]"
- News format: "N) **[Title]**\\n   - 来源：[source/domain] | [complete URL]\\n   - 影响：[impact]"
- Project format: "N) **[Project Name]**\\n   - GitHub：[complete URL]\\n   - 为什么关注：[reason]"
- Idea format: "N) **[Idea Title]**\\n   - 灵感：[description]"
- Keep URLs as plain full text after the label so readers can copy them even if WeChat does not support external links.
- Use "---" separator between sections
- Do NOT use nested bold markers (e.g., **Date:** **value**)
- **CRITICAL: Do NOT include ANY selection logic, meta-commentary, or reasoning notes in the output.**
  - NO phrases like: "选取理由", "为何选择", "同一URL两篇文章", "产业新闻选取", "note:", "注:", "说明:"
  - The report should contain ONLY the final curated content, NOT the decision-making process

**Content:**
{news_context}

**Papers:**
{papers_context}

{history_constraint}

{papers_constraint}"""

    # For English version, add extra constraint to use the exact papers from papers_context
    en_constraint = ""
    if language == "en":
        en_constraint = "CRITICAL: You MUST use the EXACT papers from the Papers section below. Do NOT invent new papers or change paper titles. Preserve all arXiv links exactly as provided (complete URLs like http://arxiv.org/abs/2604.xxxxx). Translate Chinese titles to English, but keep the same papers."
    
    user_prompt = f"Generate a {lang_instruction} GeoAI daily report following the structure above. Include 3-5 academic papers from peer-reviewed sources (arxiv.org, top conferences like CVPR/NeurIPS/IGARSS, or journals like Nature/IEEE TGRS), 3-5 diverse news items (max 2 from same domain, include application-focused news), 4-5 open source projects, and 3 new ideas. CRITICAL: Top Papers section MUST NOT contain blog posts or company announcements - only academic papers. {en_constraint}"

    # Try each API provider in order until one succeeds
    for provider in api_providers:
        provider_name = provider.get("name", "unknown")
        api_url = f"{provider['api_base_url'].rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": provider.get("model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }

        response = None
        try:
            print(f"Trying API provider: {provider_name} ({api_url})")
            response = robust_fetch.robust_post(api_url, headers=headers, json=payload, max_retries=3, timeout=120)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            history_db.update_history_from_content(content)
            print(f"Successfully used API provider: {provider_name}")
            return content
        except Exception as e:
            print(f"API provider {provider_name} failed: {e}")
            if response is not None:
                print(f"Status Code: {response.status_code}")
                print(f"Response Content: {response.text[:500]}...")
            print(f"Trying next provider...")
            continue

    print("All API providers failed")
    return None


def main():
    config = load_config()
    today = datetime.date.today().isoformat()

    use_domestic = True

    print("Fetching Arxiv papers...")
    papers_context = arxiv_fetcher.fetch_arxiv_papers()

    print("Fetching industry news...")
    news_fetcher_inst = news_fetcher.NewsFetcher(config.get("exa_api_key"))
    news_items = news_fetcher_inst.fetch_industry_news(use_domestic=use_domestic)

    news_context = ""
    if news_items:
        for item in news_items:
            news_context += f"- Title: {item['title']}\n  Date: {item['date']}\n  URL: {item['url']}\n  Summary: {str(item.get('summary', ''))[:300]}...\n\n"
    else:
        news_context = "No specific news found. Please search for general recent updates in Spatial Intelligence."

    print(f"Generating Chinese report for {today}...")
    content_zh = generate_content(config, today, papers_context, news_context, language="zh")

    if content_zh:
        # Validate and fix arXiv links
        content_zh = validate_and_fix_arxiv_links(content_zh, papers_context)
        
        year = today[:4]
        month = today[5:7]
        day = today[8:10]
        output_dir = os.path.join(os.path.dirname(__file__), year, month, day)
        os.makedirs(output_dir, exist_ok=True)
        filename_zh = f"geoai_world-model_dashboard_{today}.md"
        filepath_zh = os.path.join(output_dir, filename_zh)
        with open(filepath_zh, 'w', encoding='utf-8') as f:
            f.write(content_zh)
        print(f"Successfully generated (ZH): {filepath_zh}")
    else:
        print("Failed to generate Chinese content.")

    print(f"Generating English report for {today}...")
    content_en = generate_content(config, today, papers_context, news_context, language="en")

    if content_en:
        # Validate and fix arXiv links (extra important for EN version)
        content_en = validate_and_fix_arxiv_links(content_en, papers_context)
        
        year = today[:4]
        month = today[5:7]
        day = today[8:10]
        output_dir = os.path.join(os.path.dirname(__file__), year, month, day)
        os.makedirs(output_dir, exist_ok=True)
        filename_en = f"geoai_world-model_dashboard_en_{today}.md"
        filepath_en = os.path.join(output_dir, filename_en)
        with open(filepath_en, 'w', encoding='utf-8') as f:
            f.write(content_en)
        print(f"Successfully generated (EN): {filepath_en}")
    else:
        print("Failed to generate English content.")


if __name__ == "__main__":
    main()
