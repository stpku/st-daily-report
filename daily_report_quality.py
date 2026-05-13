"""Quality gates and run artifacts for generated daily reports."""

from __future__ import annotations

import datetime as _dt
import difflib
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse

import path_utils
import report_utils


REQUIRED_SECTIONS = {
    "zh": [
        "## 今日判断",
        "## A) Top Papers",
        "## B) Industry News",
        "## C) 工具 / 数据 / 开源更新",
        "## D) 问题线索 / 创新机会",
    ],
    "en": [
        "## Today's Read",
        "## A) Top Papers",
        "## B) Industry News",
        "## C) Tools / Data / Open Source Updates",
        "## D) Problem Leads / Innovation Opportunities",
    ],
}

RISKY_FOOTER_TERMS = [
    "扫码",
    "二维码",
    "加微信",
    "添加微信",
    "回复领取",
    "私信领取",
]


@dataclass
class ValidationResult:
    """Structured result for a single generated report validation pass."""

    language: str
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, object] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.blockers

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _runtime_json_path(*parts: str) -> str:
    path_utils.ensure_runtime_dirs()
    directory = os.path.join(path_utils.RUNTIME_DIR, *parts[:-1])
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, parts[-1])


def _normalize_for_similarity(content: str) -> str:
    lines = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"^(Date|日期)[：:]\s*\d{4}-\d{2}-\d{2}$", line, flags=re.I):
            continue
        lines.append(re.sub(r"\s+", " ", line))
    return "\n".join(lines)


def clean_markdown_artifacts(content: str) -> str:
    """Remove common LLM markdown artifacts without touching intended bold labels."""
    cleaned = content.replace("\r\n", "\n").replace("\r", "\n")

    # LLMs sometimes italicize original English titles inside Chinese parentheses:
    # （*English Title*） -> （English Title）
    cleaned = re.sub(r"（\*([^*\n（）]+)\*）", r"（\1）", cleaned)
    cleaned = re.sub(r"\(\*([^*\n()]+)\*\)", r"(\1)", cleaned)

    # Remove stray single asterisks while preserving markdown bold markers.
    cleaned = re.sub(r"(?<!\*)\*(?!\*)", "", cleaned)

    # Collapse accidental double spaces inside parenthesized English titles.
    def _compact_parenthetical(match: re.Match) -> str:
        inner = re.sub(r"[ \t]{2,}", " ", match.group(1)).strip()
        return f"（{inner}）"

    cleaned = re.sub(r"（([^）\n]{10,220})）", _compact_parenthetical, cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip() + "\n"


def _extract_domains(content: str) -> list[str]:
    domains: list[str] = []
    for url in re.findall(r"https?://[^\s)）\]]+", content):
        parsed = urlparse(url.rstrip(".,;，。；"))
        if parsed.netloc:
            domains.append(parsed.netloc.lower())
    return domains


def _previous_date(date_str: str) -> str:
    target = _dt.date.fromisoformat(date_str)
    return (target - _dt.timedelta(days=1)).isoformat()


def _compare_with_previous_day(content: str, date_str: str, language: str) -> tuple[float, str | None]:
    previous_path = report_utils.build_output_path(_previous_date(date_str), language)
    if not os.path.exists(previous_path):
        return 0.0, None
    with open(previous_path, "r", encoding="utf-8") as f:
        previous = f.read()
    current_norm = _normalize_for_similarity(content)
    previous_norm = _normalize_for_similarity(previous)
    if len(current_norm) < 1000 or len(previous_norm) < 1000:
        return 0.0, previous_path
    ratio = difflib.SequenceMatcher(None, current_norm, previous_norm).ratio()
    return ratio, previous_path


def validate_report(content: str, date_str: str, language: str) -> ValidationResult:
    """Run lightweight pre-save checks that protect the scheduled pipeline."""
    result = ValidationResult(language=language)
    sections = REQUIRED_SECTIONS.get(language, REQUIRED_SECTIONS["en"])
    missing = [section for section in sections if section not in content]
    if missing:
        result.blockers.append(f"missing required sections: {', '.join(missing)}")

    single_star_count = len(re.findall(r"(?<!\*)\*(?!\*)", content))
    if single_star_count:
        result.warnings.append(f"found {single_star_count} stray single '*' markdown markers")

    urls = re.findall(r"https?://[^\s)）\]]+", content)
    bare_arxiv_urls = [
        url for url in urls
        if re.match(r"https?://arxiv\.org/?$", url.rstrip("/"), flags=re.I)
    ]
    if bare_arxiv_urls:
        result.blockers.append("found unresolved bare arXiv URLs")

    domains = _extract_domains(content)
    domain_counts = {domain: domains.count(domain) for domain in sorted(set(domains))}
    academic_aggregators = {"arxiv.org", "www.arxiv.org"}
    overused_domains = [
        domain for domain, count in domain_counts.items()
        if count > 2 and domain not in academic_aggregators
    ]
    if overused_domains:
        result.warnings.append(f"source domains appear more than twice: {', '.join(overused_domains)}")

    similarity, previous_path = _compare_with_previous_day(content, date_str, language)
    if similarity >= 0.985:
        result.blockers.append(
            f"content is {similarity:.1%} similar to previous day report: {previous_path}"
        )

    risky_terms = [term for term in RISKY_FOOTER_TERMS if term in content]
    if risky_terms:
        result.warnings.append(f"contains high-risk CTA terms: {', '.join(risky_terms)}")

    result.metrics.update(
        {
            "sha256": _sha256_text(content),
            "char_count": len(content),
            "url_count": len(urls),
            "domain_counts": domain_counts,
            "previous_similarity": round(similarity, 4),
            "previous_report": previous_path,
        }
    )
    return result


def save_source_cache(date_str: str, papers_context: str, news_items: list[dict]) -> str:
    """Persist raw daily inputs so failed or suspicious runs can be replayed."""
    payload = {
        "target_date": date_str,
        "saved_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "papers_context_sha256": _sha256_text(papers_context),
        "papers_context": papers_context,
        "news_count": len(news_items),
        "news_items": news_items,
    }
    path = _runtime_json_path("source_cache", f"{date_str}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    return path


def save_run_manifest(date_str: str, manifest: dict[str, object]) -> str:
    payload = {
        "target_date": date_str,
        "saved_at": _dt.datetime.now().isoformat(timespec="seconds"),
        **manifest,
    }
    path = _runtime_json_path("manifests", f"{date_str}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    return path
