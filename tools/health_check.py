#!/usr/bin/env python3
"""Read-only health checks for the ST-dailyreport scheduled task.

This script is intentionally conservative: it validates the production entry
points and local file contracts without calling network APIs, publishing to
WeChat, writing reports, or touching Git remotes.
"""

from __future__ import annotations

import json
import py_compile
import re
import shutil
import sqlite3
import sys
import ast
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "governance_manifest.json"
CONFIG_DIR = ROOT / "config"
DB_PATH = ROOT / "runtime" / "state" / "history.db"

CONFIG_KEYS = ["api_providers", "wx_app_id", "wx_app_secret"]

# Required columns for history database tables
DB_SCHEMA = {
    "papers": ["id", "title", "title_norm", "arxiv_id", "url", "added_at"],
    "projects": ["id", "name", "name_norm", "url", "added_at"],
    "news_urls": ["id", "url", "added_at"],
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _load_manifest(errors: list[str]) -> dict:
    if not MANIFEST_PATH.exists():
        errors.append("missing governance_manifest.json")
        return {}
    try:
        return json.loads(_read_text(MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        errors.append(f"governance_manifest.json is not valid JSON: {exc}")
        return {}


def _is_glob_or_directory(relative: str) -> bool:
    return any(char in relative for char in "*?[") or relative.endswith("/")


def _check_required_files(errors: list[str]) -> None:
    manifest = _load_manifest(errors)
    active_files = manifest.get("active_source", [])
    state_files = manifest.get("local_runtime_state", [])
    for relative in [*active_files, *state_files]:
        if _is_glob_or_directory(relative):
            continue
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing required file: {relative}")


def _check_bat_contract(errors: list[str]) -> None:
    bat_path = ROOT / "run_daily_schedule.bat"
    if not bat_path.exists():
        return

    manifest = _load_manifest(errors)
    content = _read_text(bat_path)
    normalized_content = re.sub(r"\s+", " ", content.replace("/", "\\").lower())

    preflight = manifest.get("scheduled_preflight", {})
    preflight_command = preflight.get("command", "")
    if preflight_command:
        normalized_preflight = preflight_command.replace("/", "\\").lower()
        if normalized_preflight not in normalized_content:
            errors.append(f"scheduled batch is missing preflight: {preflight_command}")

    skip_env = preflight.get("skip_env", "")
    if skip_env and skip_env.lower() not in content.lower():
        errors.append(f"scheduled batch is missing preflight skip env: {skip_env}")

    for command in manifest.get("scheduled_commands", []):
        pattern = re.escape(command).replace(r"\ ", r"\s+")
        if not re.search(pattern, content, flags=re.IGNORECASE):
            errors.append(f"scheduled batch is missing command: {command}")

    if "exit /b 0" not in content.lower():
        errors.append("scheduled batch does not end with exit /b 0")


def _check_python_compile(errors: list[str]) -> None:
    manifest = _load_manifest(errors)
    python_files = [
        relative
        for relative in manifest.get("active_source", [])
        if relative.endswith(".py")
    ]
    for relative in python_files:
        path = ROOT / relative
        if not path.exists():
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"python compile failed: {relative}: {exc.msg}")


def _check_local_imports(errors: list[str]) -> None:
    manifest = _load_manifest(errors)
    active_files = set(manifest.get("active_source", []))
    active_python = [
        relative
        for relative in active_files
        if relative.endswith(".py") and (ROOT / relative).exists()
    ]

    for relative in active_python:
        path = ROOT / relative
        try:
            tree = ast.parse(_read_text(path))
        except SyntaxError:
            continue

        imported_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_names.add(node.module.split(".")[0])

        for name in sorted(imported_names):
            candidate = f"{name}.py"
            if (ROOT / candidate).exists() and candidate not in active_files:
                errors.append(
                    f"local import is not listed as active_source: {relative} imports {candidate}"
                )


def _check_config_shape(errors: list[str], warnings: list[str]) -> None:
    config_path = CONFIG_DIR / "config_secret.json"
    if not config_path.exists():
        return
    try:
        data = json.loads(_read_text(config_path))
    except json.JSONDecodeError as exc:
        errors.append(f"config/config_secret.json is not valid JSON: {exc}")
        return

    for key in CONFIG_KEYS:
        if key not in data:
            errors.append(f"config/config_secret.json missing key: {key}")

    if not data.get("api_providers"):
        warnings.append("config/config_secret.json has no configured api_providers")


def _check_footer_images(errors: list[str]) -> None:
    footer_path = CONFIG_DIR / "footer_intro.md"
    if not footer_path.exists():
        return

    for image_ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", _read_text(footer_path)):
        image_path = Path(image_ref)
        if not image_path.is_absolute():
            image_path = footer_path.parent / image_path
        if not image_path.exists():
            errors.append(f"footer image missing: {image_ref}")


def _check_history_db_schema(errors: list[str]) -> None:
    """Validate history.db schema matches expected columns.
    
    Regression check: ensures init_db migration added required columns
    like title_norm and name_norm to existing databases.
    """
    if not DB_PATH.exists():
        return
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        for table, expected_cols in DB_SCHEMA.items():
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                actual_cols = {row[1] for row in cursor.fetchall()}
                missing = set(expected_cols) - actual_cols
                if missing:
                    errors.append(f"history.db table '{table}' missing columns: {sorted(missing)}")
            except sqlite3.OperationalError as exc:
                errors.append(f"history.db error checking table '{table}': {exc}")
        
        conn.close()
    except sqlite3.OperationalError as exc:
        errors.append(f"history.db schema check failed: {exc}")


def _check_local_tools(warnings: list[str]) -> None:
    if shutil.which("git") is None:
        warnings.append("git executable not found on PATH; git_push.py may fail in the scheduler")


def _check_report_archive(errors: list[str], warnings: list[str]) -> None:
    archive_dir = ROOT / "2026"
    if not archive_dir.exists():
        errors.append("report archive directory missing: 2026")
        return

    reports = list(archive_dir.rglob("geoai_world-model_dashboard_*.md"))
    if not reports:
        warnings.append("no generated daily report markdown files found under 2026")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    _check_required_files(errors)
    _check_bat_contract(errors)
    _check_python_compile(errors)
    _check_local_imports(errors)
    _check_config_shape(errors, warnings)
    _check_footer_images(errors)
    _check_history_db_schema(errors)
    _check_local_tools(warnings)
    _check_report_archive(errors, warnings)

    print("ST-dailyreport health check")
    for warning in warnings:
        print(f"WARN: {warning}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("OK: scheduled task contract is intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
