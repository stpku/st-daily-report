# GeoAI + World Model Compact Dashboard
Date: 2026-01-25
Scope: GeoAI (Spatial Intelligence) + World Model (Generative 3D & Simulation)
Priorities: 3D Generation / Urban Foundation Models / Climate Agents
Format: Compact dashboard (Fresh Insights)

---

## A. Top GeoAI Papers of the Day/Week (Focus: AAAI 2026 & Foundation Models)

| Title | Source | Date | One-line Insight | Link |
|-------|--------|------|------------------|------|
| **WorldGrow: Generating Infinite 3D World** | **AAAI 2026 Oral** | 2026-01 | **Oral Presentation**. Infinite 3D scene generation for open-world games/simulations. | https://github.com/world-grow/WorldGrow |
| **BIGCity: Universal Spatiotemporal Model** | ICDE 2025 | 2025-12 | Unified trajectory & traffic state analysis model. | https://arxiv.org/abs/2412.00953 |
| **UltraSTF: Ultra-Compact Forecasting Model** | arXiv | 2025-02 | Efficient large-scale forecasting, suitable for edge/mobile deployment. | https://arxiv.org/abs/2502.20634 |
| **LLaVA-ST: Multimodal LLM for ST Understanding** | CVPR 2025 | 2025 | Fine-grained spatial-temporal localization with vision-language models. | https://github.com/appletea233/LLaVA-ST |
| **Oryx: MLLM for On-Demand ST Understanding** | ICLR 2025 | 2025 | Arbitrary resolution spatial-temporal understanding. | https://github.com/oryx-mllm/oryx |
| **Cross City Traffic Flow Generation (RAG-Diffusion)** | NeurIPS 2025 | 2025 | Retrieval-Augmented Diffusion for zero-shot cross-city transfer. | https://openreview.net/forum?id=pydeKTMrJr |
| **CropClimateX: Multi-source Crop Data Cube** | Scientific Data | 2026-01-20 | Benchmark for climate-sensitive agricultural modeling. | https://www.nature.com/articles/s41597-026-06611-x |
| **GlobalBuildingMap: 3m Global Building Footprints** | Scientific Data | 2026-01-16 | 800k satellite images processed for global mapping. | https://www.nature.com/articles/s41597-026-06578-9 |

---

## B. Industry & Application News (Spatial Intelligence Explosion)

| Org/Media | Title | Date | Relevance | Link |
|-----------|-------|------|-----------|------|
| **World Labs** | **Fei-Fei Li launches "Marble" Platform** | 2026-01 | Generates high-fidelity, persistent 3D worlds from multimodal inputs. | https://www.worldlabs.ai/ |
| **DeepMind** | **Genie 2: Foundation World Model** | 2026-01 | Creates endless playable 3D game worlds. "Action-driven" world generation. | https://deepmind.google/discover/blog/genie-2/ |
| **Tencent** | **HunyuanWorld-1.0 Released** | 2026-01 | Immersive 3D world generation from text/pixels. Open weights available. | https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0 |
| **Stanford** | **Spatial Intelligence Project Update** | 2026-01 | New roadmap for "Embodied AI" understanding physical world physics. | https://spatialintelligence.stanford.edu/ |
| **GeoAI Newsletter** | GeoAI Trends for 2026 | 2026-01-21 | Key trends: 3D Generative AI, On-orbit Edge AI, and Climate Agents. | https://geoai.substack.com/p/geoai-january-2026-newsletter |
| **WeChat** | **UrbanComp: 2026 Outlook** | 2026-01-20 | Focus on "Urban Foundation Models" and "Human-Centric Sensing". | https://mp.weixin.qq.com/ |

---

## C. High-Value Open Source Projects (New Releases)

### 3D World Models & Generation
| Project | Tech Stack | Why Important | Status | Link |
|---------|------------|---------------|--------|------|
| **WorldGrow** | Python, 3D Gen | **AAAI 2026 Oral**. Infinite world generation capability. | Active | https://github.com/world-grow/WorldGrow |
| **HunyuanWorld-1.0** | Python, 3D Gen | Tencent's open-source 3D foundation model. | Active | https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0 |
| **Hunyuan3D-2** | Python, Diffusion | High-res 3D asset generation. High fidelity. | Active | https://github.com/Tencent-Hunyuan/Hunyuan3D-2 |
| **WorldGen** | Python, Text-to-3D | Fast generation of 3D scenes (Seconds). | Active | https://github.com/ZiYang-xie/WorldGen |

### Spatial Intelligence & Robotics
| Project | Tech Stack | Why Important | Status | Link |
|---------|------------|---------------|--------|------|
| **SpatialVLA** | Python, Robotics | **RSS 2025**. Trained on 1.1M real robot episodes. | Active | https://github.com/SpatialVLA/SpatialVLA |
| **STAR** | Python, Video SR | **ICCV 2025**. Spatio-temporal augmentation for video super-res. | Active | https://github.com/NJU-PCALab/STAR |
| **MaGRITTe** | PyTorch, 3D | Meta's Masked Geometric Image Transformer. | Active | https://github.com/facebookresearch/magritte |

---

## D. 3 New Ideas (Emerging Themes: 3D Agents & Urban FMs)

### Idea 1: "Sim-to-Real" Urban Planning Agent via WorldGrow
**Concept**: Use **WorldGrow** (AAAI 2026) to generate infinite variations of *future city layouts* based on policy constraints (e.g., "maximize green space", "minimize traffic noise").
**Innovation**: Instead of static simulation, use the *generative* world model to "dream" thousands of city configurations.
**Agentic Workflow**:
1. **Generator**: WorldGrow creates 3D city blocks.
2. **Evaluator**: **UltraSTF** (Forecasting model) predicts traffic/air quality for each generated block.
3. **Optimizer**: RL agent selects the best "dreamed" block for real-world construction proposal.
**Impact**: Accelerates urban design from months to minutes.

### Idea 2: "Time-Travel" Climate Education using Genie 2
**Concept**: Leverage **DeepMind Genie 2** to create playable 3D worlds representing *historical* or *future* climate scenarios.
**Application**: A "Playable Climate Report". Users don't just read about 2050 sea-level rise; they *play* in a generated 3D world where the sea level is +2m.
**Tech Stack**: Genie 2 (World Generation) + Prithvi WxC (Climate Data injection).
**Key Feature**: "Action-driven" - Users can build levees in the game and see if they hold against the simulated storm surge.

### Idea 3: Spatial-Language "Search Engine" for Physical Assets
**Concept**: A retrieval system for large-scale physical environments (factories, cities) using **LLaVA-ST** and **Oryx**.
**Problem**: "Find the broken pipe near the red valve" is hard for current systems.
**Solution**:
1. **Indexing**: Process CCTV/Drone video feeds with **Oryx** (Arbitrary resolution ST understanding).
2. **Querying**: User asks natural language questions.
3. **Localization**: LLaVA-ST localizes the object in space and time.
**Use Case**: Industrial inspection, Smart City incident retrieval.

---

## Changelog
- **2026-01-25**: Created new dashboard focusing on AAAI 2026 and new 3D World Models (Genie 2, Marble, WorldGrow).
- **2026-01-25**: Added "Spatial Intelligence" section reflecting the shift from pure GIS to Embodied AI.
