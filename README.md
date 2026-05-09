# ST-dailyreport

GeoAI / 时空智能 / World Model 每日日报自动化项目。

## 当前生产链路

Windows 定时任务入口：

```powershell
D:\04code\code\ST-dailyreport\run_daily_schedule.bat
```

执行顺序：

1. `python run_daily_report.py`
2. `python git_push.py`
3. `python daily_task_win.py`

批处理会在正式执行前运行只读健康检查；紧急手动恢复时可设置
`SKIP_GOVERNANCE_HEALTH_CHECK=1` 跳过。

日报归档输出在 `2026/YYYY/MM/DD/` 下，包含中文和英文 Markdown。
运行态日志与临时调试产物集中在 `runtime/` 下，活跃配置与页脚素材集中在 `config/` 下。

## 治理护栏

生产入口和清理边界记录在：

- `GOVERNANCE.md`
- `governance_manifest.json`

清理、重构或移动文件前后，先运行：

```powershell
python tools\health_check.py
python tools\governance_audit.py --strict
```

这两个检查都是只读的，不会生成日报、发布微信草稿或推送 Git。

## 重要约束

- `config/config_secret.json`、`runtime/state/history.db`、`runtime/` 下的日志与调试产物都是本地运行态，不应提交。
- `wechat_sync.py` 是当前日报同步到微信公众号草稿的 active 模块。
- 不要在未通过健康检查前移动 `run_daily_schedule.bat` 依赖的文件。
