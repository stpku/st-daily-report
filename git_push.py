#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Git push helper - add, commit, push to Gitee"""

import subprocess
import datetime
import os
import sys

PROJECT_DIR = r"D:\04code\code\ST-dailyreport"

def main():
    os.chdir(PROJECT_DIR)

    subprocess.run(["git", "add", "."], check=True)

    today = datetime.date.today().isoformat()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    ).stdout

    if status.strip():
        subprocess.run(
            ["git", "commit", "-m", f"Daily report {today}"],
            check=True
        )
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print(f"Pushed to Gitee: {today}")
    else:
        print("No changes to commit.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
