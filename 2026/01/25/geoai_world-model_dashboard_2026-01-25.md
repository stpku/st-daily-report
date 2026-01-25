# GeoAI + 世界模型 紧凑型仪表盘
Date: 2026-01-25
Scope: GeoAI（EO/遥感/地理空间AI） + 世界模型（兼顾通用机器人与自动驾驶）
Priorities: 城市 / 交通 / 电信 / 农业（含中文来源）
Format: Compact dashboard（各15–20条）

---

## A. 今日/本周 GeoAI 顶级论文（15–20）

| 标题 | 来源 | 日期 | 一行洞见 | 链接 |
|------|------|------|----------|------|
| GraphCast：10天全球天气预测 | Science | 2023-12 | ML天气预测里程碑，<1分钟生成10天预报 | https://www.science.org/doi/10.1126/science.adi2336 |
| FourCastNet：NVIDIA天气预测FM | NVIDIA | 2025-07 | 6h步长，稳定预测超过1年模拟时间 | https://docs.nvidia.com/nim/earth-2/fourcastnet/latest/overview.html |
| Pangu-Weather：华为盘古气象模型 | ECMWF | 2024 | 视觉Transformer架构，10天预报 | https://ecmwf.int/en/forecasts/dataset/machine-learning-model-data |
| ClimaX：气候世界模型 | Microsoft | 2023 | 异构数据集预训练，灵活扩展 | https://proceedings.mlr.press/v202/nguyen23a.html |
| Aurora：地球系统FM | Microsoft | 2024 | 多变量大气预测，适应性微调 | https://microsoft.github.io/aurora/intro.html |
| Prithvi WxC：23亿参数气候FM | IBM/NASA | 2024 | 160变量，MERRA-2数据预训练 | https://arxiv.org/abs/2409.13598 |
| Earth AI：跨模态推理FM | arXiv | 2025-10 | 行星尺度影像+人口+环境联合建模 | https://arxiv.org/html/2510.18318v3 |
| PAN：通用交互式世界模型 | arXiv | 2025-11 | 长时程预测，GLP架构，LLM+Diffusion | https://arxiv.org/html/2511.09057v1 |
| CropClimateX：多源气象+遥感作物数据立方 | Scientific Data | 2026-01-20 | 农业时空建模与气候敏感任务基准 | https://www.nature.com/articles/s41597-026-06611-x |
| GlobalBuildingMap：全球建筑3m分辨率 | Scientific Data | 2026-01-16 | 80万卫星影像，深度学习全球建筑制图 | https://www.nature.com/articles/s41597-026-06578-9 |
| 美国地下水深度高分估计（ML, 30m） | Communications Earth & Environment | 2026-01-14 | 城市/农业水资源风险评估 | https://www.nature.com/articles/s43247-025-03094-3 |
| 全球复合沿海洪灾风险（0.1°） | Communications Earth & Environment | 2026-01-08 | 城市灾害韧性与规划 | https://www.nature.com/articles/s43247-025-03155-7 |
| STGMS：多尺度时空图神经网络 | Nature Scientific Reports | 2025-07 | 交通流多尺度特征分解 | https://www.nature.com/articles/s41598-025-11072-0 |
| AST-DGCN：自适应时空动态图卷积 | Nature Scientific Reports | 2025-07 | 自注意力动态图生成，时空误差校正 | https://www.nature.com/articles/s41598-025-12261-7 |
| PI-STGNN：物理信息时空图网络 | ICML | 2025 | 物理约束（流守恒、周期性） | https://icml.cc/virtual/2025/50687 |
| HiSTM：层次化时空Mamba | arXiv | 2025-08 | 电信蜂窝流量，Mamba高效长程依赖 | https://arxiv.org/html/2508.09184v1 |
| FARM：遥感FM精细调优 | arXiv | 2025-10 | 30m分辨率，Prithvi-EO-2.0-600M | https://arxiv.org/abs/2510.26609 |
| UniCrop：通用作物估产数据工程管道 | arXiv | 2026-01 | 多源环境数据，自动清洗和谐波 | https://arxiv.org/abs/2601.01655 |
| SkySense++ | Nature Machine Intelligence | 2025 | 多模态时序遥感FM（SAR+光学） | https://github.com/kang-wu/SkySensePlusPlus |

**中文顶刊**（7条）

| 标题 | 来源 | 日期 | 一行洞见 | 链接 |
|------|------|------|----------|------|
| 论无所不在的时空智能 | 遥感学报 | 2025 | 时空智能概念与大规模时空数据建模 | https://www.ygxb.ac.cn/rc-pub/front/front-article/download/100405943/lowqualitypdf/%E8%AE%BA%E6%97%A0%E6%89%80%E4%B8%8D%E5%9C%A8%E7%9A%84%E6%97%B6%E7%A9%BA%E6%99%BA%E8%83%BD.pdf |
| 时空智能助推新质生产力发展 | 科技导报 | 2025-12 | 李德仁院士论时空智能 | http://www.kjdb.org/CN/10.3981/j.issn.1000-7857.2024.12.01817 |
| 2025全球时空智能大会专题 | CCF/中国计算机学会 | 2025-10 | 世界模型专题论坛 | https://www.ccf.org.cn/YOCSEF/News/2025-10-12/849421.shtml |
| 中国空间智能大会World Model专题 | ChinaSI | 2025-07 | 4D世界模型，生成式世界模型 | https://www.csig.org.cn/23/202507/52769.html |
| GeoAI驱动的时空预测进展与趋势 | 地球信息科学学报 | 2025-01 | GeoAI综述，统计学习→深度学习→生成式 | https://www.dqxxkx.cn/CN/10.12082/dqxxkx.2025.240718 |
| 遥感时空知识图谱驱动的智能净化 | 地球信息科学学报 | 2025-02 | SkySense+SeqGPT+RAG，变化检测虚警剔除 | https://www.dqxxkx.cn/CN/abstract/article/1560-8999/70370 |
| AlphaEarth Foundations：遥感基础大模型潜力与挑战 | 遥感学报 | 2025-10 | 遥感基础大模型综述 | https://www.dqxxkx.cn/CN/10.12082/dqxxkx.2025.250426 |

---

## B. 今日权威产业与应用资讯（15–20）

| 机构/媒体 | 标题 | 日期 | 相关性 | 链接 |
|-----------|------|------|--------|------|
| Bloomberg | AI天气模型提升预报精度与时长 | 2026-01-22 | Google/Microsoft/NVIDIA竞争，影响城市/交通与灾害场景部署 | https://www.bloomberg.com/news/features/2026-01-22/how-ai-weather-models-are-making-better-forecasts |
| GetMapping | 2026关键地理空间趋势 | 2026-01-22 | "AI成为工作流"，GeoAI可靠性依赖高质量时序影像与高程 | https://www.getmapping.co.uk/geospatial-trends-2026/ |
| GeoAI Substack | GeoAI 2026 Newsletter | 2026-01-21 | 月度行业动态汇总 | https://geoai.substack.com/p/geoai-january-2026-newsletter |
| USGS | Landsat飞行运维引入AI/ML（CRADA） | 2026-01-15 | 提升遥感任务稳定性与数据可用性 | https://www.usgs.gov/centers/eros/news/usgs-partners-aiml-experts-improve-landsat-flight-operations |
| NVIDIA | CES 2026 Rubin平台，Earth-2开放模型/NIM提及 | 2026-01-05 | 世界模型服务化，利好电信云与城市仿真 | https://blogs.nvidia.com/blog/2026-ces-special-presentation/ |
| KDNuggets | 2026年图神经网络5大突破 | 2026-01-22 | 动态图网络用于交通/通信网络实时预测 | https://www.kdnuggets.com/5-breakthroughs-in-graph-neural-networks-to-watch-in-2026 |
| Mapbox | GeoAI 2026四大预测：Agent、MCP、Live Data | 2026-01 | 地理空间将成为LLM搜索查询核心能力 | https://www.mapbox.com/blog/geoai-in-2026-four-predictions-on-agents-mcp-and-live-data |
| GeoAI Conference | GeoAI 2026国际会议征稿 | 2026-06 | 第一届GeoAI国际会议，根特大学，投稿截止2026-02-03 | https://geoaiconference.org/ |
| Nokia | 5G上行流量AI革命准备 | 2025-08-18 | AI驱动流量预测与网络优化 | https://www.nokia.com/blog/the-ai-revolution-preparing-for-a-surge-in-5g-uplink-traffic/ |
| Farmonaut | 2026年玉米估产5大技术趋势 | 2026-01-18 | 70%玉米估产将使用遥感+AI | https://farmonaut.com/precision-farming/estimating-corn-yield-5-powerful-tech-trends-for-2026 |
| ECMWF | ML模型数据：GraphCast/Pangu-Weather/FourCastNet | 2024 | 10天预报，0.25°分辨率 | https://ecmwf.int/en/forecasts/dataset/machine-learning-model-data |
| Meteomatics | Weather API集成FourCastNet/GraphCast | 2024-05 | 商业天气API，<2秒生成7天预报 | https://meteomatics.com/en/weather-api/fourcastnet-graphcast-now-available |
| 中国国家遥感中心 | 2025全球时空智能大会 | 2025-05-23 | 世界模型专题，商业航天/低空经济 | https://www.ncsti.gov.cn/kjdt/scyq/zgckxc/zgcdt/202505/t20250523_205669.html |
| 超图软件 | SuperMap GeoAI产品升级 | 2025-Q4 | 国产GIS平台集成时空智能 | https://www.supermap.com/cn/ |
| 阿里云 | 遥感智能服务升级 | 2025-Q4 | 阿里云视觉AI接入遥感数据 | https://www.aliyun.com/product/imagerecognition |

---

## C. 高价值开源项目（15–20）

**世界模型/天气/气候**（8条）

| 项目 | 聚焦领域 | 为何重要 | 许可证/维护状态 | 链接 |
|------|----------|----------|-----------------|------|
| FourCastNet | NVIDIA天气预测FM/NIM | 6h全球预测，服务化部署 | NVIDIA License/活跃 | https://docs.nvidia.com/nim/earth-2/fourcastnet/latest/overview.html |
| GraphCast | Google DeepMind天气预测 | 开源模型，<1分钟10天预报 | MIT/活跃 | https://github.com/deepmind/graphcast |
| Pangu-Weather | 华为盘古气象模型 | 视觉Transformer，10天预报 | 需申请/活跃 | https://github.com/198808xc/Pangu-Weather |
| ClimaX | Microsoft气候FM | 多任务气候建模基座 | MIT/活跃 | https://github.com/microsoft/ClimaX |
| Aurora | Microsoft地球系统FM | 多变量大气预测 | MIT/活跃 | https://github.com/microsoft/aurora |
| Prithvi WxC | IBM/NASA气候FM | 23亿参数，160变量 | Apache-2.0/活跃 | https://github.com/IBM/Prithvi-WxC |
| WeatherBench/WeatherBench2 | 天气ML基准数据集 | 标准化评测基线 | CC-BY-4.0/活跃 | https://github.com/pangeo-data/WeatherBench |
| PySTEPS | 降水临近预报 | 业务化临近预报工具 | BSD-3/活跃 | https://github.com/py-steps/pysteps |

**遥感FM**（7条）

| 项目 | 聚焦领域 | 为何重要 | 许可证/维护状态 | 链接 |
|------|----------|----------|-----------------|------|
| SkySense | 多模态RSFM | 2150万时序SAR+光学，CVPR24 | 研究许可/活跃 | https://github.com/Jack-bo1220/SkySense |
| SkySense++ | 语义增强多模态RSFM | Nature Machine Intelligence 2025，Few-shot | 研究许可/活跃 | https://github.com/kang-wu/SkySensePlusPlus |
| OlmoEarth | AllenAI多模态EO FM | SOTA性能，NGO应用 | Apache-2.0/活跃 | https://allenai.org/blog/olmoearth-models |
| Prithvi-EO-2.0 | Hugging Face时空FM | 420万时序样本，30m分辨率 | Apache-2.0/活跃 | https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0 |
| Copernicus-FM | 统一哨兵FM | 1870万对齐图像，多任务评测 | 研究许可/活跃 | https://github.com/zhu-xlab/Copernicus-FM |
| RingMo/RingMo-Sense | 遥感FM | 时空预测，TGRS2023 | MIT/活跃 | https://github.com/AIRCAS/ringmo |
| CropSTS | 作物分类RSFM | ETH苏黎世，PASTIS-R SOTA | Apache-2.0/活跃 | https://www.research-collection.ethz.ch/handle/20.500.11850/749270 |

**时空预测/图网络**（9条）

| 项目 | 聚焦领域 | 为何重要 | 许可证/维护状态 | 链接 |
|------|----------|----------|-----------------|------|
| TorchGeo | 地理空间ML数据/采样/变换/预训练 | 加速变化检测与时序任务 | MIT/活跃 | https://github.com/torchgeo/torchgeo |
| Raster Vision | 端到端遥感CV框架 | STAC/ONNX/分布式，城市/农业分割 | Apache-2.0/活跃 | https://github.com/azavea/raster-vision |
| eo-learn | 遥感时空序列处理 | 管线化云检测/配准/特征 | MIT/活跃 | https://github.com/sentinel-hub/eo-learn |
| Spacetimeformer | 时空Transformer | 交通/通用时序预测 | MIT/活跃 | https://github.com/QData/spacetimeformer |
| STEP | 预训练增强时空图网络 | SIGKDD22，时序预训练+STGNN | MIT/活跃 | https://github.com/zezhishao/STEP |
| SGP | 可扩展时空图网络 | AAAI23，训练免费编码器 | MIT/活跃 | https://github.com/Graph-Machine-Learning-Group/sgp |
| TSL (TorchSpatiotemporal) | PyTorch时空GNN库 | GNN+时空统一框架 | MIT/活跃 | https://github.com/TorchSpatiotemporal/tsl |
| Neural STPP | Facebook时序点过程 | Neural ODE，地震/流行病/城市移动 | MIT/活跃 | https://github.com/facebookresearch/neural_stpp |
| DSTPP | Tsinghua FIB时空扩散点过程 | KDD23，Diffusion-based事件预测 | Apache-2.0/活跃 | https://github.com/tsinghua-fib-lab/Spatio-temporal-Diffusion-Point-Processes |

**中文生态**（2条）

| 项目 | 聚焦领域 | 为何重要 | 许可证/维护状态 | 链接 |
|------|----------|----------|-----------------|------|
| PaddleRS | 国内遥感套件 | 中文生态友好，快速工程化 | Apache-2.0/活跃 | https://github.com/PaddlePaddle/PaddleRS |
| mmseg/mmcv RS管线 | 视觉分割/遥感适配 | 城市与交通场景，OpenMMLab生态 | Apache-2.0/活跃 | https://github.com/open-mmlab/mmsegmentation |

**自动驾驶/机器人世界模型**（3条）

| 项目 | 聚焦领域 | 为何重要 | 许可证/维护状态 | 链接 |
|------|----------|----------|-----------------|------|
| Waymax | Waymo自动驾驶仿真 | 大规模闭环评估 | 需申请/活跃 | https://github.com/waymo-research/waymax |
| nuPlan | DriverAI规划基准 | 15k小时真实规划数据 | 需申请/活跃 | https://github.com/nv-tlabs/nuPlan_devkit |
| CARLA | 自动驾驶仿真平台 | 开源仿真器 | MIT/活跃 | https://github.com/carla-simulator/carla |

---

## D. 3个新创意（GeoAI + 世界模型）

### 创意1：灾害触发与级联风险的事件型世界模型

**Problem**：城市/农业地区面临灾害（洪涝、火险、滑坡）触发与级联风险，现有预测多为连续时空建模，缺乏对稀疏事件（触发时刻）与因果链（级联扩散）的联合建模。

**Approach**：
- 融合遥感FM嵌入（Copernicus-FM/SkySense/OlmoEarth）捕捉地表状态
- 注入外生驱动：Earth-2/GraphCast/Pangu-Weather气象/气候情景
- 事件过程建模：Neural STPP / Diffusion STPP（稀疏触发 + 时空扩散）
- 不确定性校准：Bayesian Neural Fields (BayesNF)

**Data**：
- Sentinel-1/2、Landsat（地表状态）
- ERA5/Earth-2（气象驱动）
- OSM（基础设施与人口暴露）
- 历史灾害事件库（emer、GDACS）

**Baseline/Eval**：
- 对比传统灾害指数（NDVI异常、火险气象指数、洪涝淹没模型）
- 指标：事件提前量、F1@Recall、ECE校准、CRPS

**First Experiment Checklist**：
1. 数据采集与清洗（5类数据源，对齐时空分辨率）
2. 预训练嵌入提取（固定Copernicus-FM/OlmoEarth）
3. 事件标注与强度编码（历史灾害事件）
4. STPP模型训练与消融（嵌入 vs 嵌入+气象驱动）
5. 评测与可视化（灾害热点地图 + 事件概率时序）

**风险**：
- 事件标注稀缺性与分布偏移
- 多源数据时空对齐复杂度
- 外生气象驱动的滞后与误差传播

---

### 创意2：在轨主动感知的轻量世界模型编码器（CubeSat/边缘蒸馏）

**Problem**：现有在轨成像卫星缺乏实时决策能力，常拍摄云区或低价值区域，导致任务效率低、数据下传负载高。

**Approach**：
- 将时空FM（Copernicus-FM/SkySense/OlmoEarth）蒸馏为轻量边缘编码器（<100MB，<1TOPS）
- 集成动态指向策略（NASA Dynamic Targeting概念）：实时评分下一景价值（云覆盖率 + 事件热点 + 历史价值）
- 决策策略：云区规避 + 热点追踪 + 兴趣区域优先

**Data**：
- 蒸馏数据：Sentinel-2/Landsat时序 + 云掩膜 + 事件热点标签
- 边缘模型：量化后的Transformer编码器（8-bit/4-bit）
- 任务目标：最大化可用影像率、最小化响应时延、约束能耗预算

**Baseline/Eval**：
- 对比随机拍摄、固定任务规划、传统云检测后调度
- 指标：可用影像比例、热点捕获率、边缘推理延迟、能耗

**First Experiment Checklist**：
1. 教师模型选择（SkySense++ vs OlmoEarth vs Copernicus-FM）
2. 蒸馏策略设计（特征蒸馏 + 输出logits + 时序对比损失）
3. 边缘部署适配（TensorRT-Lite / TFLite / ONNX quantized）
4. 仿真环境测试（CubeSat姿态动力学 + 轨道预测）
5. 端到端评估（1周仿真任务 vs 基线方法）

**风险**：
- 边缘算力与内存严格约束
- 蒸馏后精度损失（尤其是稀疏事件检测）
- 实时决策的鲁棒性（极端天气、通信中断）

---

### 创意3：面向城市数字孪生的Geo-RAG + 世界模型体（交通/电信场景）

**Problem**：城市数字孪生需要融合多源时空数据（遥感、IoT、电信、交通），并提供可解释的决策支持与反事实模拟，但现有平台缺乏统一检索与因果推理能力。

**Approach**：
- 检索增强：STAC/Planetary Computer/Earth Engine + Copernicus-Embed + OSM（GeoLink）
- 知识融合：多模态嵌入对齐（遥感+地图+语义）
- 世界模型模拟：Earth-2/ClimaX/GraphCast情景驱动 + Spacetimeformer时序预测
- 可解释输出：自然语言解释 + 反事实方案（"如果增加绿地面积X%，内涝深度降低Y%"）

**Use-Cases**：
- 城市内涝模拟与绿地布局优化
- 交通拥堵预测与信号灯自适应控制
- 电信基站负载均衡与应急覆盖

**Baseline/Eval**：
- 对比传统数字孪生平台（无RAG/世界模型）
- 指标：决策采纳率、模拟精度（RMSE/MAE）、反事实合理性（专家评估）、响应时延

**First Experiment Checklist**：
1. 数据接入：STAC目录 + Earth Engine数据立方 + OSM向量层
2. 检索系统：向量检索（Copernicus-Embed）+ 规则过滤（时空约束）
3. 世界模型集成：调用Earth-2 API / 本地ClimaX推理
4. RAG Prompt设计：检索上下文 + 模拟结果 + 反事实生成
5. 场景评估：选定城市/交通/电信用例，完成基线对比

**风险**：
- 多源数据质量与一致性（云污染、时空分辨率不匹配）
- 世界模型API延迟与成本（实时场景不适用）
- 反事实推理的可信度（需物理约束或专家校验）

---

## 变更记录（Changelog）
- **2026-01-22T16:00**：创建检查点模板，确认范围（GeoAI+世界模型；城市/交通/电信/农业；含中文来源；紧凑仪表盘）
- **2026-01-22T14:30**：执行并行检索，收集论文/新闻/开源项目候选条目
- **2026-01-22T16:00**：更新检查点，补充完整候选条目清单
- **2026-01-22T23:00**：完成去重与验证，交付成品仪表盘（A/B/C各15–20条 + D创意）

---

## 附录：来源白名单与过滤规则

### 学术来源（顶刊/顶会）
- Nature系列：Nature Communications, Nature Machine Intelligence, Communications Earth & Environment, Scientific Data, npj Climate & Atmospheric Science
- Science/PNAS/Science Advances
- Remote Sensing of Environment (RSE)
- ISPRS Journal of Photogrammetry and Remote Sensing
- IEEE TGRS/GRSL
- ACM SIGSPATIAL, KDD, NeurIPS, ICLR, ICML（GeoAI/世界模型相关）
- 中文顶刊：遥感学报、测绘学报、地球信息科学学报、科技导报

### 机构来源
- 国际：NASA, ESA, Copernicus, USGS, NOAA, ECMWF, ESA Digital Twin Earth
- 国内：CMA/国家卫星气象中心, 国家遥感中心, AIRCAS（中科院空天信息创新研究院）, CCF, 中国计算机学会

### 产业来源
- Google Research (Earth AI, Geospatial Reasoning)
- NVIDIA (Earth-2, FourCastNet, NIM)
- Microsoft (Planetary Computer, Aurora, ClimaX)
- Esri (GeoAI, Real-Time Spatial AI)
- 华为（盘古气象）
- 超图, 阿里云, 百度智能云, Nokia

### 开源来源
- 国际：torchgeo, raster-vision, eo-learn, Copernicus-FM, SkySense/++, OlmoEarth, ClimaX, FourCastNet, GraphCast, WeatherBench2, Neural STPP, DSTPP, Spacetimeformer, STEP, SGP, TSL
- 国内：PaddleRS, mmsegmentation/mmcv, 武大/中院团队开源项目
- 自动驾驶：Waymax, nuPlan, CARLA

### 过滤规则
- **日期**：今日（2026-01-22）优先；近7日次之；近期（Jan 2026）顶刊论文
- **权威性**：需有明确机构/期刊/厂商原始发布
- **可验证**：提供可访问的原始链接
- **去重**：同一事件/论文取最权威来源
- **中文来源**：优先官方渠道（政府/机构/厂商），媒体需交叉验证原始出处

---

*本仪表盘版本：2026-01-22（最终交付版）*
