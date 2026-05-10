"""LLM client: multi-provider API rotation for report generation."""

from __future__ import annotations

from dataclasses import dataclass, field

import history_db
import robust_fetch
from log import logger
from report_prompting import (
    build_history_constraints,
    build_system_prompt,
    build_user_prompt,
    get_language_settings,
)


@dataclass
class ReportRequest:
    """Typed container for the inputs needed to generate one report."""

    date_str: str
    papers_context: str
    news_context: str
    language: str = "zh"


@dataclass
class ApiProvider:
    """One LLM provider entry from config."""

    name: str = "unknown"
    api_base_url: str = ""
    api_key: str = ""
    model: str = "gpt-3.5-turbo"


def _build_prompts(req: ReportRequest) -> tuple[str, str]:
    """Construct system and user prompts from a report request."""
    settings = get_language_settings(req.language)
    lang_instruction = settings["lang_instruction"]

    recent_projects = history_db.get_recent_projects()
    recent_papers = history_db.get_recent_papers_titles()
    history_constraint, papers_constraint = build_history_constraints(
        recent_projects=recent_projects,
        recent_papers=recent_papers,
    )

    system_prompt = build_system_prompt(
        date_str=req.date_str,
        settings=settings,
        news_context=req.news_context,
        papers_context=req.papers_context,
        history_constraint=history_constraint,
        papers_constraint=papers_constraint,
    )
    user_prompt = build_user_prompt(lang_instruction, req.language)
    return system_prompt, user_prompt


def _call_provider(provider: ApiProvider, system_prompt: str, user_prompt: str) -> str | None:
    """Try a single provider; return content or None."""
    api_url = f"{provider.api_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {provider.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
    }

    response = None
    try:
        logger.info("Trying API provider: %s (%s)", provider.name, api_url)
        response = robust_fetch.robust_post(
            api_url, headers=headers, json=payload, max_retries=3, timeout=120,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        logger.info("Successfully used API provider: %s", provider.name)
        return content
    except Exception as e:
        logger.warning("API provider %s failed: %s", provider.name, e)
        if response is not None:
            logger.debug("Status Code: %s", response.status_code)
            logger.debug("Response Content: %s", response.text[:500])
        return None


def generate_content(config, date_str, papers_context, news_context, language="zh"):
    """Call LLM API providers in rotation until one succeeds.

    Backward-compatible signature — wraps arguments into ``ReportRequest``.
    """
    raw_providers = config.get("api_providers", [])
    if not raw_providers:
        logger.error("No API providers configured")
        return None

    providers = [
        ApiProvider(
            name=p.get("name", "unknown"),
            api_base_url=p.get("api_base_url", ""),
            api_key=p.get("api_key", ""),
            model=p.get("model", "gpt-3.5-turbo"),
        )
        for p in raw_providers
    ]

    req = ReportRequest(
        date_str=date_str,
        papers_context=papers_context,
        news_context=news_context,
        language=language,
    )
    system_prompt, user_prompt = _build_prompts(req)

    for provider in providers:
        content = _call_provider(provider, system_prompt, user_prompt)
        if content is not None:
            return content
        logger.info("Trying next provider...")

    logger.error("All API providers failed")
    return None
