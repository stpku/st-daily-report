#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Git push helper - add, commit, push to Gitee"""

import subprocess
import datetime
import os
import sys

import path_utils
from log import logger

PROJECT_DIR = path_utils.ROOT_DIR

def main():
    os.chdir(PROJECT_DIR)

    # Only stage daily report outputs — code changes should be committed separately.
    subprocess.run(["git", "add", "2026/"], check=True)

    today = datetime.date.today().isoformat()

    # Check if there are actually staged changes in 2026/ (not the whole worktree).
    diff_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", "2026/"],
        capture_output=True, text=True,
    )
    has_staged_changes = diff_result.returncode != 0

    if has_staged_changes:
        subprocess.run(
            ["git", "commit", "-m", f"Daily report {today}"],
            check=True
        )
        subprocess.run(["git", "push", "origin", "master"], check=True)
        logger.info("Pushed to Gitee: %s", today)
    else:
        logger.info("No staged changes in 2026/ to commit.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
