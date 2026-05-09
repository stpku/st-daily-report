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
import json

# 添加脚本目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 导入依赖模块
import arxiv_fetcher
import news_fetcher
import auto_generate_ai
import history_db
import path_utils


def load_config():
    """加载配置文件"""
    config_file = path_utils.resolve_path(
        path_utils.config_path('config_secret.json'),
        os.path.join(SCRIPT_DIR, 'config_secret.json'),
    )
    if not os.path.exists(config_file):
        print(f"❌ 错误：配置文件不存在 {config_file}")
        sys.exit(1)
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """主函数"""
    print("=" * 60)
    print("📊 ST-Dailyreport 每日日报生成")
    print("=" * 60)
    
    # 获取日期（如果是当天运行，使用当天日期）
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = datetime.date.today().isoformat()
    
    print(f"📅 生成日期：{target_date}")
    
    # 加载配置
    config = load_config()
    
    # 检查网络环境
    use_domestic = True
    try:
        import socket
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("export.arxiv.org", 443))
        print("✅ arXiv.org 可访问")
        use_domestic = False
    except Exception:
        print("⚠️  arXiv.org 不可访问，使用国内镜像")
        use_domestic = True
    
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
    
    news_context = ""
    if news_items:
        for item in news_items:
            news_context += f"- Title: {item['title']}\n  Date: {item['date']}\n  URL: {item['url']}\n  Summary: {str(item.get('summary', ''))[:300]}...\n\n"
        print(f"✅ 获取到 {len(news_items)} 条新闻")
    else:
        print("⚠️  未获取到新闻，使用通用提示")
        news_context = "No specific news found. Please search for general recent updates in Spatial Intelligence."
    
    # 3. 生成中文版日报
    print("\n✍️  步骤 3/4: 生成中文版日报...")
    content_zh = auto_generate_ai.generate_content(
        config, target_date, papers_context, news_context, language="zh"
    )
    
    if content_zh:
        # 验证并修复 arXiv 链接
        content_zh = auto_generate_ai.validate_and_fix_arxiv_links(content_zh, papers_context)
        
        # 保存文件
        year = target_date[:4]
        month = target_date[5:7]
        day = target_date[8:10]
        output_dir = os.path.join(SCRIPT_DIR, year, month, day)
        os.makedirs(output_dir, exist_ok=True)
        
        filename_zh = f"geoai_world-model_dashboard_{target_date}.md"
        filepath_zh = os.path.join(output_dir, filename_zh)
        
        with open(filepath_zh, 'w', encoding='utf-8') as f:
            f.write(content_zh)
        
        print(f"✅ 中文版已保存：{filepath_zh}")
    else:
        print("❌ 生成中文版失败")
        sys.exit(1)
    
    # 4. 生成英文版日报
    print("\n✍️  步骤 4/4: 生成英文版日报...")
    content_en = auto_generate_ai.generate_content(
        config, target_date, papers_context, news_context, language="en"
    )
    
    if content_en:
        # 验证并修复 arXiv 链接
        content_en = auto_generate_ai.validate_and_fix_arxiv_links(content_en, papers_context)
        
        # 保存文件
        year = target_date[:4]
        month = target_date[5:7]
        day = target_date[8:10]
        output_dir = os.path.join(SCRIPT_DIR, year, month, day)
        os.makedirs(output_dir, exist_ok=True)
        
        filename_en = f"geoai_world-model_dashboard_en_{target_date}.md"
        filepath_en = os.path.join(output_dir, filename_en)
        
        with open(filepath_en, 'w', encoding='utf-8') as f:
            f.write(content_en)
        
        print(f"✅ 英文版已保存：{filepath_en}")
    else:
        print("❌ 生成英文版失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ ST-Dailyreport 生成完成！")
    print("=" * 60)
    print(f"\n📁 输出目录：{output_dir}")
    print(f"📄 中文版：{filename_zh}")
    print(f"📄 英文版：{filename_en}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
