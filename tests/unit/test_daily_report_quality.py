import json
import os

import daily_report_quality


def _valid_zh_report(date_str="2026-05-10"):
    return f"""# GeoAI & World Model Daily Insight
Date: {date_str}
## 今日判断
- 遥感检索评测开始强调可控对照。
- 世界模型开始进入具身规划评测。
- 应用新闻更偏向灾害和环境监测。
今日关键词: 遥感检索 / 世界模型 / 评测 / 环境监测

---

## A) Top Papers（精选 3-5 篇）
1) **测试论文**（Test Paper）
   - 原文：arXiv | https://arxiv.org/abs/2605.01234v1
   - 为什么重要：提供一个可复现评测入口。

---

## B) Industry News（产业动态，精选 3-5 条）
1) **测试新闻**（Test News）
   - 来源：example.com | https://example.com/news
   - 影响：给出应用场景线索。

---

## C) 工具 / 数据 / 开源更新
今日无高置信度新增工具。

---

## D) 问题线索 / 创新机会
1) **遥感检索可控评测**
   - 机会：问题 → 场景 → 原型方向
"""


def test_clean_markdown_artifacts_removes_italic_title_markers():
    content = "1) **标题**（*Rethinking Electro-Optical Vision Foundation Models*）\n"

    cleaned = daily_report_quality.clean_markdown_artifacts(content)

    assert "（Rethinking Electro-Optical Vision Foundation Models）" in cleaned
    assert "*Rethinking" not in cleaned


def test_validate_report_accepts_valid_zh_report(monkeypatch):
    monkeypatch.setattr(
        daily_report_quality.report_utils,
        "build_output_path",
        lambda date_str, language: os.path.join("missing", "report.md"),
    )

    result = daily_report_quality.validate_report(_valid_zh_report(), "2026-05-10", "zh")

    assert result.ok
    assert result.blockers == []
    assert result.metrics["url_count"] == 2


def test_validate_report_blocks_duplicate_previous_day(tmp_path, monkeypatch):
    previous = tmp_path / "previous.md"
    previous.write_text(_valid_zh_report("2026-05-09") * 20, encoding="utf-8")
    monkeypatch.setattr(
        daily_report_quality.report_utils,
        "build_output_path",
        lambda date_str, language: str(previous),
    )

    result = daily_report_quality.validate_report(
        _valid_zh_report("2026-05-10") * 20,
        "2026-05-10",
        "zh",
    )

    assert not result.ok
    assert any("similar" in blocker for blocker in result.blockers)


def test_save_source_cache_writes_replayable_json(tmp_path, monkeypatch):
    monkeypatch.setattr(daily_report_quality.path_utils, "RUNTIME_DIR", str(tmp_path))

    path = daily_report_quality.save_source_cache(
        "2026-05-10",
        "paper context",
        [{"title": "News", "url": "https://example.com"}],
    )

    payload = json.loads((tmp_path / "source_cache" / "2026-05-10.json").read_text(encoding="utf-8"))
    assert path.endswith(os.path.join("source_cache", "2026-05-10.json"))
    assert payload["news_count"] == 1
    assert payload["papers_context"] == "paper context"
