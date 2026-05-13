LANGUAGE_SETTINGS = {
    "zh": {
        "lang_instruction": "Chinese (Simplified)",
        "title_format": "# GeoAI & World Model Daily Insight",
        "scope_line": "**Scope:** GeoAI（空间智能/遥感/GIS+AI）+ World Model（3D生成与通用模拟/具身智能）",
        "priorities_text": "## 今日判断",
        "mainline_label": "今日主线",
        "keyword_label": "今日关键词",
        "header_example_keywords": "AOD / Sentinel-2 / 物理世界模型 / 可信预测",
        "label_source": "原文",
        "label_why_important": "为什么重要",
        "label_news_source": "来源",
        "label_impact": "影响",
        "label_project_url": "项目地址",
        "label_why_follow": "为什么关注",
        "label_opportunity": "机会",
        "section_papers_desc": "精选 3-5 篇",
        "section_news_desc": "产业动态，精选 3-5 条",
        "papers_title_instruction": "Chinese translation + original English title",
        "news_title_instruction": "**Chinese translation + original English title**",
        "papers_format": 'N) **Chinese Title**（English Title）\\n   - {label_source}：[Source] | [complete URL]\\n   - {label_why_important}：[one-sentence insight]',
        "news_format": 'N) **Chinese Title**（English Original Title）\\n   - {label_news_source}：[source/domain] | [complete URL]\\n   - {label_impact}：[impact]',
        "section_c_title": "工具 / 数据 / 开源更新",
        "section_d_title": "问题线索 / 创新机会",
    },
    "en": {
        "lang_instruction": "English",
        "title_format": "# GeoAI + World Model Compact Dashboard",
        "scope_line": "**Scope:** GeoAI (Spatial Intelligence) + World Model (3D Generation & Simulation)",
        "priorities_text": "## Today's Read",
        "mainline_label": "Main Thread",
        "keyword_label": "Keywords",
        "header_example_keywords": "AOD / Sentinel-2 / physical world models / calibrated forecasting",
        "label_source": "Source",
        "label_why_important": "Why it matters",
        "label_news_source": "Source",
        "label_impact": "Impact",
        "label_project_url": "Project URL",
        "label_why_follow": "Why it matters",
        "label_opportunity": "Opportunity",
        "section_papers_desc": "3-5 selected papers",
        "section_news_desc": "Industry highlights, 3-5 items",
        "papers_title_instruction": "English title (original)",
        "news_title_instruction": "**English Original Title**",
        "papers_format": 'N) **English Title**\\n   - {label_source}: [Source] | [complete URL]\\n   - {label_why_important}: [one-sentence insight]',
        "news_format": 'N) **English Title**\\n   - {label_news_source}: [source/domain] | [complete URL]\\n   - {label_impact}: [impact]',
        "section_c_title": "Tools / Data / Open Source Updates",
        "section_d_title": "Problem Leads / Innovation Opportunities",
    },
}

SYSTEM_PROMPT_TEMPLATE = """Generate a GeoAI Daily Dashboard for date: {date_str}.

**CRITICAL INSTRUCTION - HEADER FORMAT:**
1. First line MUST be the report title in format: {title_format}
2. DO NOT place any news titles or content in the header
3. The header should only contain:
   - Line 1: {title_format}
   - Line 2: Date: {date_str} (plain text, NO bold markers)
   - Line 3: {priorities_text}
   - Line 4: {mainline_label}: one sentence, no more than 40 Chinese characters or 22 English words
   - Lines 5-7: exactly 3 bullet points, each explaining a concrete trend or judgment
   - Line 8: {keyword_label}: keyword1 / keyword2 / keyword3 / keyword4
4. Lines 9-11: Blank line
5. Lines 12+: News context (for generating content)

**Structure Requirements:**
1. Header: Title only (on first line), Date (plain text), {priorities_text}, {mainline_label}, 3 bullets, {keyword_label} (one short line)
    - Format example:
      {title_format}
      Date: {date_str}
      {priorities_text}
      {mainline_label}: one crisp sentence...
      - Point 1...
      - Point 2...
      - Point 3...
      {keyword_label}: {header_example_keywords}
    - IMPORTANT: Do NOT use Scope in the header. Keep the first screen short and scannable on mobile.
    - Each judgment must name the concrete object and implication. Avoid generic phrases such as "值得关注", "持续发展", or "具有重要意义" unless followed by a specific reason.
    - Each judgment should fit in 1-2 mobile lines. Use "object: change, implication" style when possible.
    - Scope reference for this report family: {scope_line}

2. Section A: Top Papers（{section_papers_desc}）- 3-5 papers with {papers_title_instruction} + {label_source} + {label_why_important}
   **CRITICAL CONSTRAINT: Top Papers MUST ONLY contain academic papers from peer-reviewed sources: arxiv.org, top-tier conferences (CVPR, ICCV, ECCV, NeurIPS, ICLR, AAAI, IJCAI, SIGGRAPH, IGARSS, ISPRS), or top journals (Nature, Science, IEEE TGRS, Remote Sensing of Environment, ISPRS Journal). DO NOT include blog posts, company announcements, or non-academic news articles.**
   **CRITICAL: You MUST choose Top Papers ONLY from the Papers block below. Do NOT introduce well-known older papers from memory. Preserve the exact title and exact source link from papers_context; you may translate the title into Chinese, but the English title and URL must remain the provided paper.**
   **CRITICAL: You MUST preserve the exact source links from the input papers_context. DO NOT fabricate, truncate, or modify paper links. Each {label_source} field must contain the complete URL, NOT just a homepage.**

3. Section B: Industry News（{section_news_desc}）- 1-5 news items with {news_title_instruction} + {label_news_source} + {label_impact}
   **CRITICAL CONSTRAINT: Diversify news sources - maximum 2 items from the same company/domain (e.g., max 2 from openai.com). Prioritize application-focused news (agriculture, urban planning, disaster response, environmental monitoring, drone/satellite applications) over pure AI model announcements. Skip weakly related finance/crypto/general market items unless the GeoAI or World Model relevance is direct and concrete.**
   If there are fewer than 3 high-confidence directly relevant news items, use fewer items instead of filling the section with generic AI marketing, hiring, finance, or speech content.
4. Section C: {section_c_title} - 0-5 items with Name + {label_project_url} + {label_why_follow}. Prefer real releases, datasets, paper code, model/tool updates, or projects that connect to today's paper/news themes; avoid generic repeat items unless there is a direct reason today. If there is no high-value update, write one compact sentence and do not force filler.
5. Section D: {section_d_title} - 1-3 grounded opportunities with Title + {label_opportunity}. These should come from today's papers/news/tools and describe a concrete problem, scenario, and possible collaboration or product direction. Do not call this section "OPC机会".

**Format Requirements:**
- Use markdown format with proper hierarchy
- Paper format: "{papers_format}"
- In Chinese output, prefer putting the Chinese title in the bold title and the original English title inside parentheses after it; keep the English title plain, not bold or italic.
- Do NOT wrap the English paper title in italic or bold markers inside the parentheses.
- News format: "{news_format}"
- Tool/Data/Open-source format: "N) **[Name]**\\n   - {label_project_url}：[complete URL]\\n   - {label_why_follow}：[reason]"
- Problem/opportunity format: "N) **[Opportunity Title]**\\n   - {label_opportunity}：[problem → scenario → possible prototype or collaboration direction]"
- Keep URLs as plain full text after the label so readers can copy them even if WeChat does not support external links.
- Do not wrap original English titles in single asterisks. Never output italic markers in titles.
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


def get_language_settings(language: str) -> dict:
    return LANGUAGE_SETTINGS.get(language, LANGUAGE_SETTINGS["en"])


def build_history_constraints(
    recent_projects: list[str] | None = None,
    recent_papers: list[str] | None = None,
) -> tuple[str, str]:
    recent_projects = recent_projects or []
    recent_papers = recent_papers or []

    history_constraint = ""
    if recent_projects:
        project_list_str = ", ".join(recent_projects)
        history_constraint = (
            "CRITICAL: Do NOT suggest the following open source projects as they were "
            f"recently featured: {project_list_str}. Find DIFFERENT relevant projects."
        )

    papers_constraint = ""
    if recent_papers:
        paper_list_str = ", ".join(recent_papers[:10])
        papers_constraint = (
            "CRITICAL: Do NOT suggest the following papers as they were recently featured: "
            f"{paper_list_str}. Find DIFFERENT relevant papers."
        )

    return history_constraint, papers_constraint


def build_user_prompt(lang_instruction: str, language: str) -> str:
    exact_papers_constraint = (
        "CRITICAL: Top Papers must be selected from the Papers block exactly. "
        "Do not use papers from model memory, even if they are famous or relevant."
    )
    en_constraint = ""
    if language == "en":
        en_constraint = (
            "CRITICAL: You MUST use the EXACT papers from the Papers section below. "
            "Do NOT invent new papers or change paper titles. Preserve all source links "
            "exactly as provided. Translate Chinese titles to English, but keep the same papers."
        )

    return (
        f"Generate a {lang_instruction} GeoAI daily report following the structure above. "
        "Include 3-5 academic papers from peer-reviewed sources (arxiv.org, top conferences "
        "like CVPR/NeurIPS/IGARSS, or journals like Nature/IEEE TGRS), 3-5 diverse news items "
        "(max 2 from same domain, include application-focused news), 0-5 tool/data/open-source "
        "updates only when they are genuinely relevant, and 1-3 problem leads / innovation "
        "opportunities. Do not use the phrase OPC机会. CRITICAL: Top Papers section MUST NOT "
        "contain blog posts or company announcements - only academic papers. "
        f"{exact_papers_constraint} {en_constraint}"
    )


def build_system_prompt(
    date_str: str,
    settings: dict,
    news_context: str,
    papers_context: str,
    history_constraint: str,
    papers_constraint: str,
) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        date_str=date_str,
        title_format=settings["title_format"],
        scope_line=settings["scope_line"],
        priorities_text=settings["priorities_text"],
        mainline_label=settings["mainline_label"],
        keyword_label=settings["keyword_label"],
        header_example_keywords=settings["header_example_keywords"],
        label_source=settings["label_source"],
        label_why_important=settings["label_why_important"],
        label_news_source=settings["label_news_source"],
        label_impact=settings["label_impact"],
        label_project_url=settings["label_project_url"],
        label_why_follow=settings["label_why_follow"],
        label_opportunity=settings["label_opportunity"],
        section_papers_desc=settings["section_papers_desc"],
        section_news_desc=settings["section_news_desc"],
        section_c_title=settings["section_c_title"],
        section_d_title=settings["section_d_title"],
        papers_title_instruction=settings["papers_title_instruction"],
        news_title_instruction=settings["news_title_instruction"],
        papers_format=settings["papers_format"],
        news_format=settings["news_format"],
        news_context=news_context,
        papers_context=papers_context,
        history_constraint=history_constraint,
        papers_constraint=papers_constraint,
    )
