# GeoAI + 世界模型 紧凑型仪表盘
Date: 2026-01-26
Scope: GeoAI (空间智能) + World Model (3D生成与模拟)
Priorities: 3D生成 / 城市基础模型 / 气候智能体
Format: 紧凑仪表盘 (最新洞见)

---

## A. 今日/本周 GeoAI 顶级论文 (聚焦 AAAI 2026 & 基础模型)

| 标题 | 来源 | 日期 | 一行洞见 | 链接 |
|------|------|------|----------|------|
| **WorldGrow: 生成无限3D世界** | **AAAI 2026 Oral** | 2026-01 | **Oral展示**。面向开放世界游戏/模拟的无限3D场景生成。 | https://github.com/world-grow/WorldGrow |
| **BIGCity: 通用时空模型** | ICDE 2025 | 2025-12 | 统一轨迹与交通状态分析的通用模型。 | https://arxiv.org/abs/2412.00953 |
| **UltraSTF: 超紧凑时空预测模型** | arXiv | 2025-02 | 高效大规模预测，适合边缘/移动端部署。 | https://arxiv.org/abs/2502.20634 |
| **LLaVA-ST: 多模态大模型时空理解** | CVPR 2025 | 2025 | 基于视觉-语言模型的细粒度时空定位。 | https://github.com/appletea233/LLaVA-ST |
| **Oryx: 按需时空理解MLLM** | ICLR 2025 | 2025 | 任意分辨率的时空理解多模态大模型。 | https://github.com/oryx-mllm/oryx |
| **跨城市交通流生成 (RAG-Diffusion)** | NeurIPS 2025 | 2025 | 基于检索增强扩散模型的零样本跨城市迁移。 | https://openreview.net/forum?id=pydeKTMrJr |
| **CropClimateX: 多源作物数据立方** | Scientific Data | 2026-01-20 | 气候敏感型农业建模基准数据集。 | https://www.nature.com/articles/s41597-026-06611-x |
| **GlobalBuildingMap: 全球建筑3m制图** | Scientific Data | 2026-01-16 | 处理80万景卫星影像的全球建筑足迹制图。 | https://www.nature.com/articles/s41597-026-06578-9 |

---

## B. 产业与应用资讯 (空间智能爆发)

| 机构/媒体 | 标题 | 日期 | 相关性 | 链接 |
|-----------|------|------|--------|------|
| **World Labs** | **李飞飞发布 "Marble" 平台** | 2026-01 | 从多模态输入生成高保真、持久的3D世界。 | https://www.worldlabs.ai/ |
| **DeepMind** | **Genie 2: 基础世界模型** | 2026-01 | 创建无限可玩的3D游戏世界。"行动驱动"的世界生成。 | https://deepmind.google/discover/blog/genie-2/ |
| **腾讯** | **HunyuanWorld-1.0 发布** | 2026-01 | 从文本/像素生成沉浸式3D世界。权重开源。 | https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0 |
| **Stanford** | **空间智能项目更新** | 2026-01 | "具身智能"理解物理世界物理规律的新路线图。 | https://spatialintelligence.stanford.edu/ |
| **GeoAI Newsletter** | 2026年 GeoAI 趋势 | 2026-01-21 | 核心趋势：3D生成式AI、在轨边缘AI、气候智能体。 | https://geoai.substack.com/p/geoai-january-2026-newsletter |
| **微信公众号** | **UrbanComp: 2026 展望** | 2026-01-20 | 聚焦 "城市基础模型" 与 "以人为本的感知"。 | https://mp.weixin.qq.com/ |

---

## C. 高价值开源项目 (最新发布)

### 3D 世界模型与生成
| 项目 | 技术栈 | 为何重要 | 状态 | 链接 |
|------|--------|----------|------|------|
| **WorldGrow** | Python, 3D Gen | **AAAI 2026 Oral**。无限世界生成能力。 | 活跃 | https://github.com/world-grow/WorldGrow |
| **HunyuanWorld-1.0** | Python, 3D Gen | 腾讯开源3D基础模型。 | 活跃 | https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0 |
| **Hunyuan3D-2** | Python, Diffusion | 高分辨率3D资产生成。高保真度。 | 活跃 | https://github.com/Tencent-Hunyuan/Hunyuan3D-2 |
| **WorldGen** | Python, Text-to-3D | 秒级生成3D场景。 | 活跃 | https://github.com/ZiYang-xie/WorldGen |

### 空间智能与机器人
| 项目 | 技术栈 | 为何重要 | 状态 | 链接 |
|------|--------|----------|------|------|
| **SpatialVLA** | Python, Robotics | **RSS 2025**。在110万真实机器人片段上训练。 | 活跃 | https://github.com/SpatialVLA/SpatialVLA |
| **STAR** | Python, Video SR | **ICCV 2025**。用于视频超分的时空增强。 | 活跃 | https://github.com/NJU-PCALab/STAR |
| **MaGRITTe** | PyTorch, 3D | Meta 掩码几何图像Transformer。 | 活跃 | https://github.com/facebookresearch/magritte |

---

## D. 3个新创意 (新兴主题：3D智能体 & 城市FM)

### 创意 1: 基于 WorldGrow 的 "Sim-to-Real" 城市规划智能体
**概念**: 利用 **WorldGrow** (AAAI 2026) 根据政策约束（如"最大化绿地"，"最小化交通噪音"）生成无限的*未来城市布局*变体。
**创新点**: 区别于静态模拟，利用*生成式*世界模型 "梦想" 出数千种城市配置。
**智能体工作流**:
1. **生成器**: WorldGrow 创建3D城市街区。
2. **评估器**: **UltraSTF** (预测模型) 预测每个生成街区的交通/空气质量。
3. **优化器**: RL 智能体选择最佳的 "梦想" 街区作为现实建设提案。
**影响**: 将城市设计周期从数月缩短至数分钟。

### 创意 2: 基于 Genie 2 的 "时间旅行" 气候教育
**概念**: 利用 **DeepMind Genie 2** 创建代表*历史*或*未来*气候情景的可玩3D世界。
**应用**: "可玩的气候报告"。用户不仅仅阅读2050年海平面上升的报告，而是在一个海平面上升2米的生成3D世界中*游玩*。
**技术栈**: Genie 2 (世界生成) + Prithvi WxC (气候数据注入)。
**关键特性**: "行动驱动" - 用户可以在游戏中建造堤坝，看它们是否能抵挡模拟的风暴潮。

### 创意 3: 物理资产的 空间-语言 "搜索引擎"
**概念**: 利用 **LLaVA-ST** 和 **Oryx** 构建的大规模物理环境（工厂、城市）检索系统。
**痛点**: 现有系统很难处理 "找到红色阀门旁边的破损管道" 这种查询。
**方案**:
1. **索引**: 使用 **Oryx** (任意分辨率时空理解) 处理 CCTV/无人机视频流。
2. **查询**: 用户提出自然语言问题。
3. **定位**: LLaVA-ST 在空间和时间上定位对象。
**用例**: 工业巡检，智慧城市事件检索。

---

## 变更记录
- **2026-01-25**: 创建新仪表盘，聚焦 AAAI 2026 和新型 3D 世界模型 (Genie 2, Marble, WorldGrow)。
- **2026-01-25**: 增加 "空间智能" (Spatial Intelligence) 板块，反映从纯 GIS 向具身智能 (Embodied AI) 的转变。
