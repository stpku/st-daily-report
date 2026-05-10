#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ST-Dailyreport 微信同步（Windows 原生版）
功能：将中文日报同步到微信公众号草稿箱
"""

import os
import re
import sys
import datetime
import argparse

import path_utils

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = SCRIPT_DIR

FILE_PATTERN = r"geoai_world-model_dashboard_.*\.md"


def find_report(target_date: str) -> str | None:
    """Find the Chinese report for *target_date* (YYYY-MM-DD).

    Returns the full path or None when no matching file exists.
    """
    year = target_date[:4]
    month = target_date[5:7]
    day = target_date[8:10]
    target_dir = os.path.join(PROJECT_DIR, year, month, day)

    if not os.path.exists(target_dir):
        print(f"Report directory not found: {target_dir}")
        return None

    for f in os.listdir(target_dir):
        if re.match(FILE_PATTERN, f) and target_date in f and "_en_" not in f and "checkpoint" not in f:
            return os.path.join(target_dir, f)

    print(f"No Chinese report found for {target_date}")
    return None


def _resolve_target_date(date_arg: str | None) -> str:
    """Determine the target date.

    Priority:
    1. Explicit ``--date`` argument (YYYY-MM-DD)
    2. ``REPORT_DATE`` environment variable
    3. Today
    """
    if date_arg:
        return date_arg
    env_date = os.environ.get("REPORT_DATE", "").strip()
    if env_date:
        return env_date
    return datetime.date.today().isoformat()


def main():
    parser = argparse.ArgumentParser(description="Sync Chinese daily report to WeChat draft")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD). Defaults to today.")
    args = parser.parse_args()

    print("=" * 50)
    print("WeChat Sync (Windows)")
    print("=" * 50)

    target_date = _resolve_target_date(args.date)
    report_path = find_report(target_date)

    # Yesterday fallback: only when explicitly opted-in via env var
    if report_path is None and os.environ.get("WECHAT_ALLOW_YESTERDAY", "").strip() == "1":
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        print(f"WECHAT_ALLOW_YESTERDAY=1 — falling back to yesterday ({yesterday})")
        report_path = find_report(yesterday)

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
        success = syncer.sync(report_path)
        if not success:
            print("WeChat sync returned failure.")
            return 1
        print("WeChat sync completed.")
    except Exception as e:
        print(f"WeChat sync failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
