#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ST-Dailyreport 微信同步（Windows 原生版）
从 daily_task.py 适配，修正路径为 Windows 原生路径
功能：将中文日报同步到微信公众号草稿箱
"""

import os
import re
import sys
import datetime
import json
import path_utils

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = SCRIPT_DIR

FILE_PATTERN = r"geoai_world-model_dashboard_.*\.md"


def load_config():
    config_path = path_utils.resolve_path(
        path_utils.config_path('config_secret.json'),
        os.path.join(PROJECT_DIR, 'config_secret.json'),
    )
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def find_today_report():
    """找到今天的中文版日报文件"""
    today = datetime.date.today().isoformat()
    year = today[:4]
    month = today[5:7]
    day = today[8:10]
    target_dir = os.path.join(PROJECT_DIR, year, month, day)

    if not os.path.exists(target_dir):
        print(f"Report directory not found: {target_dir}")
        return None

    # 查找中文版（不含 _en_ 的）
    for f in os.listdir(target_dir):
        if re.match(FILE_PATTERN, f) and today in f and "_en_" not in f and "checkpoint" not in f:
            return os.path.join(target_dir, f)

    # fallback: 昨天的
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    year_y = yesterday[:4]
    month_y = yesterday[5:7]
    day_y = yesterday[8:10]
    target_dir_y = os.path.join(PROJECT_DIR, year_y, month_y, day_y)

    if os.path.exists(target_dir_y):
        for f in os.listdir(target_dir_y):
            if re.match(FILE_PATTERN, f) and yesterday in f and "_en_" not in f and "checkpoint" not in f:
                return os.path.join(target_dir_y, f)

    print(f"No Chinese report found for {today}")
    return None


def main():
    print("=" * 50)
    print("WeChat Sync (Windows)")
    print("=" * 50)

    report_path = find_today_report()
    if not report_path:
        print("No report to sync, skipping WeChat step.")
        return 0

    print(f"Found report: {report_path}")

    # 同步到微信公众号
    try:
        from wechat_sync import WeChatSync
        config_path = path_utils.resolve_path(
            path_utils.config_path('config_secret.json'),
            os.path.join(PROJECT_DIR, 'config_secret.json'),
        )
        syncer = WeChatSync(config_path)
        syncer.sync(report_path)
        print("WeChat sync completed.")
    except Exception as e:
        print(f"WeChat sync failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
