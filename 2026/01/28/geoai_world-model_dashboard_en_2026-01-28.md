# GeoAI + World Model Compact Dashboard
**Date:** 2026-01-28  
**Scope:** GeoAI (Spatial Intelligence, Remote Sensing, GIS+AI) + World Models (3D Generation, Simulation, Embodied AI)  
**Priorities (today):** Disaster assessment VLM benchmarks • Robust evaluation for embodied agents • Cross-modality translation for remote sensing • Programmatic/probabilistic world modeling • Data-efficient robot motion generation

---

## A. Top Papers (Arxiv Picks)

1) **DisasterInsight: A Multimodal Benchmark for Function-Aware and Grounded Disaster Assessment**  
   Link: http://arxiv.org/abs/2601.18493v1 (2026-01-26)  
   **One-line Insight:** Moves remote-sensing VLM evaluation beyond coarse labels toward *grounded*, function-aware disaster interpretation—useful for actionable damage and capability mapping.

2) **Adaptive Domain Shift in Diffusion Models for Cross-Modality Image Translation**  
   Link: http://arxiv.org/abs/2601.18623v1 (2026-01-26)  
   **One-line Insight:** Replaces a single “global” domain mapping with adaptive shift—relevant to SAR↔optical, day↔night, seasonal, and sensor-to-sensor translation workflows in GeoAI.

3) **CASSANDRA: Programmatic and Probabilistic Learning and Inference for Stochastic World Modeling**  
   Link: http://arxiv.org/abs/2601.18620v1 (2026-01-26)  
   **One-line Insight:** Combines programmatic structure with probabilistic inference for stochastic world models—an appealing template for *causal-ish* geospatial simulators and decision support.

4) **TC-IDM: Grounding Video Generation for Executable Zero-shot Robot Motion**  
   Link: http://arxiv.org/abs/2601.18323v1 (2026-01-26)  
   **One-line Insight:** Uses grounded video generation as a bridge to executable motion, pointing to a scalable path for “world-model-to-policy” transfer with less robot-specific data.

5) **Trustworthy Evaluation of Robotic Manipulation: A New Benchmark and AutoEval Methods**  
   Link: http://arxiv.org/abs/2601.18723v1 (2026-01-26)  
   **One-line Insight:** Pushes toward standardized, automated evaluation for VLA manipulation—conceptually aligned with the need for *trustworthy* evaluation of geo-foundation models.

6) **Beyond Static Datasets: Robust Offline Policy Optimization via Vetted Synthetic Transitions**  
   Link: http://arxiv.org/abs/2601.18107v1 (2026-01-26)  
   **One-line Insight:** “Vetted” synthetic transitions offer a pragmatic route to stronger offline RL—relevant to training embodied agents in simulators before limited real-world deployment.

7) **Multi-Perspective Subimage CLIP with Keyword Guidance for Remote Sensing Image-Text Retrieval**  
   Link: http://arxiv.org/abs/2601.18190v1 (2026-01-26)  
   **One-line Insight:** Tackles fine-grained alignment (subimage + keyword guidance), helpful for map search, change discovery, and “find me airports with construction” style retrieval.

---

## B. Industry News (3–5 items, with sources)

1) **Esri highlights deeper GeoAI patterns for ArcGIS workflows (foundation models, raster analytics, AI-assisted mapping).**  
   Source: https://www.esri.com/arcgis-blog/

2) **Google DeepMind shares new research updates on embodied agents and world-model learning for planning.**  
   Source: https://deepmind.google/discover/blog/

3) **NVIDIA posts new Omniverse / simulation tooling updates aimed at robotics and synthetic-data generation.**  
   Source: https://developer.nvidia.com/blog/

4) **Microsoft Research publishes new work on multimodal agents and evaluation practices for agentic systems.**  
   Source: https://www.microsoft.com/en-us/research/blog/

5) **Planet Labs updates resources for rapid satellite-driven monitoring and analytics for events and change detection.**  
   Source: https://www.planet.com/pulse/

---

## C. Open Source Projects (with URLs)

1) **TorchGeo** — PyTorch datasets/models/utilities for geospatial ML (remote sensing, tiling, sampling).  
   https://github.com/microsoft/torchgeo

2) **Raster Vision** — End-to-end pipeline for satellite/aerial imagery (chips, training, inference, eval).  
   https://github.com/azavea/raster-vision

3) **OpenMMLab MMSegmentation** — Strong semantic segmentation toolbox; widely used for RS segmentation baselines.  
   https://github.com/open-mmlab/mmsegmentation

4) **CesiumJS** — 3D geospatial visualization engine; useful front-end for world-model/scene digital twins.  
   https://github.com/CesiumGS/cesium

5) **Habitat-Sim** — Embodied AI simulator for navigation and agent evaluation; adaptable to “geo-indoors” tasks.  
   https://github.com/facebookresearch/habitat-sim

---

## D. 3 New Ideas (GeoAI × World Models)

1) **“Disaster World Model” for action-grounded damage assessment**  
   Use *DisasterInsight*-style grounding to train a model that predicts not only labels (flooded/building-damaged) but **functional affordances** (road passability, landing zones, shelter capacity) inside a lightweight simulator for response planning.

2) **Cross-sensor diffusion translator as a simulator adapter**  
   Apply adaptive domain shift diffusion to translate between **simulated renders ↔ real satellite modalities** (SAR/optical/thermal), making synthetic-data pipelines more robust for change detection and VLM grounding.

3) **Programmatic stochastic geo-sim with CASSANDRA-like structure**  
   Build a **probabilistic, rule-augmented world model** over geospatial entities (roads, powerlines, rivers, land use) where interventions (storm, policy change, construction) produce stochastic outcomes—then train planners/offline RL on vetted synthetic transitions.

---