#!/usr/bin/env python3
"""Audit root-level files against governance_manifest.json.

The audit is read-only. By default it reports unclassified files without failing.
Use --strict when a cleanup branch should enforce a fully classified root.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "governance_manifest.json"
AUDITED_SUFFIXES = {".py", ".bat", ".ps1", ".sh", ".md", ".json"}
IGNORE_NAMES = {".gitignore"}
POLICY_KEYS = {"never_commit"}
REFERENCE_GUARD_ACTION_MARKERS = ("archive", "delete", "remove", "move")
PROTECTED_LIST_KEYS = ("active_source",)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _manifest_entries(manifest: dict) -> dict[str, list[str]]:
    return {
        key: value
        for key, value in manifest.items()
        if key not in POLICY_KEYS
        and isinstance(value, list)
        and all(isinstance(item, str) for item in value)
    }


def _matches(entry: str, relative_path: str) -> bool:
    normalized = entry.replace("\\", "/")
    if normalized.endswith("/"):
        return relative_path.startswith(normalized)
    if any(char in normalized for char in "*?["):
        return fnmatch.fnmatch(relative_path, normalized)
    return relative_path == normalized


def _classify(relative_path: str, categories: dict[str, list[str]]) -> list[str]:
    matches: list[str] = []
    for category, entries in categories.items():
        if any(_matches(entry, relative_path) for entry in entries):
            matches.append(category)
    return matches


def _root_inventory() -> list[str]:
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.iterdir()
        if path.is_file() and path.name not in IGNORE_NAMES
    )


def _root_directories() -> list[str]:
    return sorted(
        f"{path.relative_to(ROOT).as_posix()}/"
        for path in ROOT.iterdir()
        if path.is_dir() and path.name not in {".git"}
    )


def _root_scripts() -> list[str]:
    script_suffixes = {".py", ".bat", ".ps1", ".sh"}
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.iterdir()
        if path.is_file() and path.suffix.lower() in script_suffixes
    )


def _is_glob_or_directory(relative: str) -> bool:
    return any(char in relative for char in "*?[") or relative.endswith("/")


def _protected_paths(manifest: dict) -> list[str]:
    protected: list[str] = []
    entry = manifest.get("production_entry")
    if isinstance(entry, str):
        protected.append(entry)

    for key in PROTECTED_LIST_KEYS:
        protected.extend(manifest.get(key, []))

    unique: list[str] = []
    seen: set[str] = set()
    for relative in protected:
        if not isinstance(relative, str) or _is_glob_or_directory(relative):
            continue
        normalized = relative.replace("\\", "/")
        if normalized in seen:
            continue
        seen.add(normalized)
        if (ROOT / normalized).is_file():
            unique.append(normalized)
    return unique


def _cleanup_candidate_scripts(manifest: dict) -> list[str]:
    candidates: list[str] = []
    for script, disposition in manifest.get("script_dispositions", {}).items():
        if disposition.get("status") == "absent_in_worktree":
            continue
        if "/" in script or "\\" in script:
            continue
        if not (ROOT / script).is_file():
            continue
        action = str(disposition.get("action", "")).lower()
        if any(marker in action for marker in REFERENCE_GUARD_ACTION_MARKERS):
            candidates.append(script)
    return sorted(candidates)


def _check_cleanup_candidates_unreferenced(manifest: dict, strict: bool) -> int:
    candidates = _cleanup_candidate_scripts(manifest)
    protected_paths = _protected_paths(manifest)
    references: list[tuple[str, str, str]] = []

    for candidate in candidates:
        candidate_name = Path(candidate).name.lower()
        candidate_stem = Path(candidate).stem
        for command in manifest.get("scheduled_commands", []):
            if candidate_name in str(command).lower():
                references.append((candidate, "scheduled_commands", "command"))
        for protected in protected_paths:
            if protected == candidate:
                continue
            protected_path = ROOT / protected
            content = protected_path.read_text(encoding="utf-8", errors="replace")
            if protected_path.suffix.lower() == ".py" and Path(candidate).suffix.lower() == ".py":
                references.extend(
                    (candidate, protected, reason)
                    for reason in _python_references(content, candidate_name, candidate_stem)
                )
            elif candidate_name in content.lower():
                references.append((candidate, protected, "text"))

    for candidate, protected, reason in references:
        print(f"REFERENCE_GUARD {candidate} referenced by {protected} ({reason})")

    if not references:
        print("OK: cleanup-candidate scripts are not referenced by active files")
        return 0

    print(f"WARN: {len(references)} cleanup-candidate references found in active files")
    return 1 if strict else 0


def _python_references(content: str, candidate_name: str, candidate_stem: str) -> list[str]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return ["unparseable-python-text"] if candidate_name in content.lower() else []

    docstring_value_ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.body and isinstance(node.body[0], ast.Expr):
                docstring_value_ids.add(id(node.body[0].value))

    reasons: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == candidate_stem:
                    reasons.append("import")
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] == candidate_stem:
                reasons.append("import")
        elif (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstring_value_ids
            and candidate_name in node.value.lower()
        ):
            reasons.append("string")
    return reasons


def _check_script_dispositions(manifest: dict, strict: bool) -> int:
    dispositions = manifest.get("script_dispositions", {})
    missing = [script for script in _root_scripts() if script not in dispositions]
    stale = [
        script
        for script, disposition in dispositions.items()
        if "/" not in script and "\\" not in script and not (ROOT / script).exists()
        and disposition.get("status") not in {"absent_in_worktree", "archived"}
    ]

    for script in missing:
        print(f"MISSING_DISPOSITION {script}")
    for script in stale:
        print(f"STALE_DISPOSITION   {script}")

    if not missing and not stale:
        print("OK: all root scripts have dispositions")
        return 0

    if missing:
        print(f"WARN: {len(missing)} root scripts are missing dispositions")
    if stale:
        print(f"WARN: {len(stale)} dispositions refer to absent root scripts")
    return 1 if strict and missing else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="fail when root files are unclassified")
    args = parser.parse_args()

    manifest = _load_manifest()
    categories = _manifest_entries(manifest)
    root_files = [*_root_inventory(), *_root_directories()]

    unclassified: list[str] = []
    overlaps: list[tuple[str, list[str]]] = []

    print(f"Governance audit: {manifest.get('project', ROOT.name)}")
    for relative in root_files:
        matches = _classify(relative, categories)
        if not matches:
            unclassified.append(relative)
            print(f"UNCLASSIFIED {relative}")
        elif len(matches) > 1:
            overlaps.append((relative, matches))
            print(f"OVERLAP      {relative}: {', '.join(matches)}")

    disposition_status = _check_script_dispositions(manifest, args.strict)
    reference_status = _check_cleanup_candidates_unreferenced(manifest, args.strict)

    if not unclassified and not overlaps and disposition_status == 0 and reference_status == 0:
        print("OK: all audited root files have exactly one governance category")
        return 0

    if overlaps:
        print(f"WARN: {len(overlaps)} files match multiple categories")
    if unclassified:
        print(f"WARN: {len(unclassified)} root files are unclassified")

    return 1 if args.strict and (unclassified or disposition_status or reference_status) else 0


if __name__ == "__main__":
    sys.exit(main())
