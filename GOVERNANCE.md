# ST-dailyreport Governance

This file defines the current cleanup guardrails. The daily scheduled task must
continue to work while the project is cleaned.

## Production Contract

The active Windows scheduled task entry is `run_daily_schedule.bat`.

It must continue to run these steps in order:

1. `python run_daily_report.py`
2. `python git_push.py`
3. `python daily_task_win.py`

Before those steps, the batch file runs the read-only governance health check
when `tools\health_check.py` exists. Set `SKIP_GOVERNANCE_HEALTH_CHECK=1` only
for emergency manual recovery.

The active source files for that path are:

- `run_daily_report.py`
- `auto_generate_ai.py`
- `arxiv_fetcher.py`
- `news_fetcher.py`
- `rss_news_fetcher.py`
- `robust_fetch.py`
- `history_db.py`
- `history_tracker.py`
- `git_push.py`
- `daily_task_win.py`
- `wechat_sync.py`
- `config/footer_intro.md`

The machine-readable version of this contract is
`governance_manifest.json`. Update that manifest first when the production
surface changes, then update this narrative file if needed.

The runtime state and local credentials are:

- `config/config_secret.json`
- `runtime/state/history.db`
- `runtime/state/history.json`
- `runtime/logs/daily_schedule.log`
- `runtime/logs/auto_generate_ai.log`
- `runtime/logs/daily_task.log`

Do not delete or move runtime state until a migration step has been tested.

## Cleanup Order

1. Keep the current scheduled task stable.
2. Track and protect the active production source files.
3. Mark old scripts as legacy only after checking they are not called by the
   batch file or imported by the active path.
4. Move generated/debug outputs out of the source surface after the health check
   passes.
5. Refactor shared rendering and fetch logic only after adding regression checks.

## Health Check

Run this before and after each cleanup slice:

```powershell
python tools\health_check.py
```

The check is read-only. It does not publish, call external APIs, write reports,
or push Git remotes.

Use this to inspect root-level governance classification:

```powershell
python tools\governance_audit.py
```

`governance_manifest.json` also records `script_dispositions` for root scripts.
Every cleanup pass should update that section before archiving or deleting a
script.

Archived root scripts are kept under `legacy/root_scripts/YYYY-MM-DD/`. A script
may move there only after `python tools\governance_audit.py --strict` confirms
that archive/delete candidates are not referenced by the active scheduled-task
files.
