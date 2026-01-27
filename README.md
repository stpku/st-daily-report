# ST-dailyreport (GeoAI & World Model Daily Insight)

## 简介 (Introduction)

本项目用于自动化生成和归档 **GeoAI (空间智能)** 与 **World Model (世界模型)** 领域的每日进展报告。

主要关注内容包括：
- **GeoAI**: 遥感、GIS、空间分析与人工智能的结合。
- **World Model**: 3D生成、通用仿真、具身智能与时空预测。

每日报告会自动发布到相关媒体渠道，并归档到本项目以及 [Awesome Spatio-Temporal AI](https://gitee.com/stpku/awesome_spatial_tempoal_ai) 列表。

## 项目结构

- `2026/`: 按年份归档的每日报告 (Markdown格式)。
- `auto_generate_ai.py`: AI辅助生成日报内容的脚本。
- `daily_task.py`: 每日任务主程序，负责处理文件、发送通知和触发归档。
- `wechat_sync.py`: 微信公众号同步工具。

## 自动化流程

1. **内容生成**: 从源（Sandbox/View）提取每日 Markdown 草稿。
2. **处理与归档**: `daily_task.py` 处理日期、格式，并归档到 `YYYY/MM/DD` 目录。
3. **通知推送**: 
   - 推送至 WxPusher (微信通知)。
   - 同步至微信公众号草稿箱。
4. **数据同步**: 自动解析 Top Papers 并同步更新到 [Awesome Spatio-Temporal AI](https://gitee.com/stpku/awesome_spatial_tempoal_ai) 仓库。

## 许可证

MIT License
