import datetime
import os

# 配置
TEMPLATE = """# GeoAI + 世界模型 紧凑型仪表盘
Date: {date}
Scope: GeoAI (空间智能) + World Model (3D生成与模拟)
Priorities: 3D生成 / 城市基础模型 / 气候智能体
Format: 紧凑仪表盘 (最新洞见)

---

## A. 今日/本周 GeoAI 顶级论文 (自动生成占位符)

| 标题 | 来源 | 日期 | 一行洞见 | 链接 |
|------|------|------|----------|------|
| **(Auto) Paper Title 1** | arXiv | {date} | 自动抓取占位符 - 需集成 arXiv API | https://arxiv.org/list/cs.AI/recent |
| **(Auto) Paper Title 2** | CVPR | {date} | 自动抓取占位符 | - |
| **(Auto) Paper Title 3** | AAAI | {date} | 自动抓取占位符 | - |

---

## B. 产业与应用资讯 (自动生成占位符)

| 机构/媒体 | 标题 | 日期 | 相关性 | 链接 |
|-----------|------|------|--------|------|
| **TechCrunch** | **(Auto) News 1** | {date} | 自动抓取占位符 | - |
| **Google Blog** | **(Auto) News 2** | {date} | 自动抓取占位符 | - |

---

## D. 3个新创意 (需人工/LLM生成)

### 创意 1: [待填充]
**概念**: ...
**应用**: ...

---

## 变更记录
- **{date}**: 自动生成的报告草稿。
"""

def generate_daily_draft():
    today = datetime.date.today().isoformat()
    output_dir = "/mnt/d/04_代码/code/sandbox/doc/view"
    filename = f"geoai_world-model_dashboard_{today}.md"
    filepath = os.path.join(output_dir, filename)
    
    # 如果文件已存在，跳过（避免覆盖人工编辑的内容）
    if os.path.exists(filepath):
        print(f"File {filename} already exists. Skipping auto-generation.")
        return

    content = TEMPLATE.format(date=today)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Generated daily draft: {filepath}")
    print("Next step: Edit the file to add specific insights, then run daily_task.py")

if __name__ == "__main__":
    generate_daily_draft()
