# GeoAI + World Model Compact Dashboard  
**Date:** 2026-01-29  
**Scope:** GeoAI (Spatial Intelligence) + World Model (3D Generation & Simulation)  
**Key Message(Today's Highlights):**  
- **No paper feed + no reliable news feed provided today** → treat this dashboard as a **strategy/ops-focused brief**: what to track, what to build, and what to prototype next.  
- **2026 execution theme:** unify **Earth observation (multi-sensor time series)** with **3D/4D world models** for forecasting, counterfactual simulation, and embodied/agent planning.

---

## A. Top Papers (Arxiv)
**Status:** No papers fetched (Error accessing Arxiv).  
**Action for tomorrow:** If you can paste the Arxiv links / titles (or enable access), I’ll select the **top 5–8** and add **one-line insights** in the required format.

---

## B. Industry News (Spatial Intelligence)
**Status:** **No major updates today.**  
*Reason:* You asked to “search for general recent updates,” but **no specific news items or source URLs were provided**. Per requirements, I **must** use the provided Source URL for each item and cannot fabricate links.

---

## C. Open Source Projects (GeoAI + World Model)
*(All projects include URLs; excludes the “recently featured” list.)*

1) **TorchGeo** — Geospatial datasets + samplers + training utilities for PyTorch (remote sensing, land cover, SSL).  
https://github.com/microsoft/torchgeo

2) **eo-learn** — Modular pipelines for Earth observation (patching, feature extraction, temporal processing) built around Sentinel data workflows.  
https://github.com/sentinel-hub/eo-learn

3) **SegFormer (official)** — Strong baseline transformer segmentation model often adapted for remote sensing and aerial imagery.  
https://github.com/NVlabs/SegFormer

4) **PyTorch3D** — Differentiable 3D operators (rendering, meshes, point clouds) useful for training 3D generative/world models.  
https://github.com/facebookresearch/pytorch3d

5) **CARLA Simulator** — Autonomous driving sim with sensors + maps; useful for bridging real geospatial context to embodied evaluation.  
https://github.com/carla-simulator/carla

---

## D. 3 New Ideas (GeoAI × World Model)
1) **“STAC-to-Scene Graph” World Model Pretraining**  
Convert EO tiles (multi-sensor, multi-temporal) into a **scene graph** (roads, buildings, vegetation, water, change events). Train a model to **predict future graph states** and **render** consistent map/imagery views.

2) **Counterfactual Urban Change Simulator (Policy-in-the-Loop)**  
A 4D city model that takes zoning + mobility + construction signals and simulates plausible futures; optimize for metrics (heat, flooding, commute). Use EO change detection as **weak supervision** to constrain realism.

3) **Embodied Agent Navigation with Satellite-to-Street Domain Bridging**  
Train an agent that plans with **satellite priors** (global context) and refines with **local 3D perception** (street-level/robot sensors). World model learns to “hallucinate” missing 3D structure from overhead cues for better exploration.

---