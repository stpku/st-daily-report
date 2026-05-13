#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ST-Dailyreport 独立执行脚本
功能：每日自动生成 GeoAI & World Model 日报
不依赖 OpenClaw，直接调用大模型 API
"""

import os
import sys
import datetime

# 添加脚本目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 导入依赖模块
import arxiv_fetcher
import news_fetcher
import auto_generate_ai
import history_db
import path_utils


def resolve_target_date(argv: list[str] | None = None) -> str:
    argv = argv or sys.argv
    if len(argv) > 1:
        return argv[1]
    return datetime.date.today().isoformat()


def build_news_context(news_items) -> str:
    if not news_items:
        return "No specific news found. Please search for general recent updates in Spatial Intelligence."

    chunks = []
    for item in news_items:
        chunks.append(
            f"- Title: {item['title']}\n"
            f"  Date: {item['date']}\n"
            f"  URL: {item['url']}\n"
            f"  Summary: {str(item.get('summary', ''))[:300]}...\n"
        )
    return "\n".join(chunks) + "\n"


def generate_and_save_report(config, target_date, papers_context, news_context, language):
    content = auto_generate_ai.generate_content(
        config, target_date, papers_context, news_context, language=language
    )
    if not content:
        return None

    content, unresolved = auto_generate_ai.validate_and_fix_arxiv_links(content, papers_context)
    if unresolved > 0:
        print(f"❌ 报告生成失败：{unresolved} 个 arXiv 链接无法解析")
        return None

    filepath = auto_generate_ai.save_report(target_date, language, content)

    return filepath


def main():
    """主函数"""
    print("=" * 60)
    print("📊 ST-Dailyreport 每日日报生成")
    print("=" * 60)
    
    # 获取日期（如果是当天运行，使用当天日期）
    target_date = resolve_target_date()
    
    print(f"📅 生成日期：{target_date}")
    
    # 加载配置
    config = path_utils.load_config()
    
    # 初始化/迁移历史数据库
    history_db.init_db()
    
    # 检查网络环境
    use_domestic = auto_generate_ai.check_domestic_network()
    
    # 1. 获取 arXiv 论文
    print("\n📚 步骤 1/4: 获取 arXiv 论文...")
    papers_context = arxiv_fetcher.fetch_arxiv_papers()
    if papers_context:
        print(f"✅ 获取到 {len(papers_context.split(chr(10)))} 篇论文")
    else:
        print("❌ 获取论文失败")
        sys.exit(1)
    
    # 2. 获取产业新闻
    print("\n📰 步骤 2/4: 获取产业新闻...")
    news_fetcher_inst = news_fetcher.NewsFetcher(config.get("exa_api_key", ""))
    news_items = news_fetcher_inst.fetch_industry_news(use_domestic=use_domestic)
    
    news_context = build_news_context(news_items)
    if news_items:
        print(f"✅ 获取到 {len(news_items)} 条新闻")
    else:
        print("⚠️  未获取到新闻，使用通用提示")
    
    # 3. 生成中文版日报
    print("\n✍️  步骤 3/4: 生成中文版日报...")
    filepath_zh = generate_and_save_report(
        config, target_date, papers_context, news_context, language="zh"
    )

    if filepath_zh:
        print(f"✅ 中文版已保存：{filepath_zh}")
    else:
        print("❌ 生成中文版失败")
        sys.exit(1)
    
    # 4. 生成英文版日报
    print("\n✍️  步骤 4/4: 生成英文版日报...")
    filepath_en = generate_and_save_report(
        config, target_date, papers_context, news_context, language="en"
    )

    if filepath_en:
        print(f"✅ 英文版已保存：{filepath_en}")
    else:
        print("❌ 生成英文版失败")
        sys.exit(1)

    # Update history only after both languages have succeeded
    # Read content from the Chinese version file
    history_ok = False
    try:
        with open(filepath_zh, 'r', encoding='utf-8') as f:
            zh_content = f.read()
        result = history_db.update_history_from_content(zh_content)
        history_ok = True
        print(f"📝 历史数据库已更新：{result['parsed_papers']} 篇论文，{result['parsed_news']} 条新闻，{result['parsed_projects']} 个项目（新增 {result['new_papers']}/{result['new_news']}/{result['new_projects']}）")
        # Warn if expected sections are empty — likely a parsing regression
        if result['parsed_papers'] == 0:
            print("⚠️  警告：未解析到任何论文，Section A 可能格式异常")
        if result['parsed_news'] == 0:
            print("⚠️  警告：未解析到任何新闻，Section B 可能格式异常")
    except Exception as e:
        print(f"⚠️  更新历史数据库时出错：{e}")
    
    print("\n" + "=" * 60)
    if history_ok:
        print("✅ ST-Dailyreport 生成完成！")
    else:
        print("⚠️  ST-Dailyreport 生成完成，但历史数据库更新失败！")
    print("=" * 60)
    output_dir = os.path.dirname(filepath_zh)
    filename_zh = os.path.basename(filepath_zh)
    filename_en = os.path.basename(filepath_en)
    print(f"\n📁 输出目录：{output_dir}")
    print(f"📄 中文版：{filename_zh}")
    print(f"📄 英文版：{filename_en}")
    
    return 0 if history_ok else 2


if __name__ == "__main__":
    sys.exit(main())
