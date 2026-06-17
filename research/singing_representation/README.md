# 🎙️ Singing Representation Research

**Research question:** Where does singer identity survive when a person moves from speech to singing, and how can we leverage that to control technique and timbre in zero-shot singing voice conversion?

This directory contains all code, design documents, and results for the **two-track master's research project** on singing representation learning.

---

## 📁 Directory Structure

```
singing_representation/
│
├── design/                     # Design documents and context for Codex
│   ├── CODEX_INSTRUCTIONS.md   # ← START HERE (Codex entry point)
│   └── links/                  # Symlinks to pro_suggestions and free_recall docs
│
├── experiments/
│   ├── track1_timbre/          # Track 1: Timbre Mode Residual Mapper
│   │   └── README.md
│   └── track2_technique/       # Track 2: Technique Probing & Reconstruction
│       └── README.md
│
├── scripts/
│   ├── data_prep/              # Data extraction and manifest building
│   ├── probing/                # Linear probes, retrieval, residual control
│   └── intervention/           # Latent steering, LoRA, Seed-VC injection
│
├── notebooks/                  # Exploratory analysis and visualization
│
├── results/                    # Output plots, tables, audio samples
│
└── README.md                   # This file
```

---

## 🚦 Track Overview

| Track | Goal | Primary Doc | Status |
|-------|------|-------------|--------|
| **Track 1: Timbre** | Map speech→singing mode residual; improve Seed-VC with speech-only reference | [pro3](../../pro_suggestions/pro3_voice_representation_idea_review.md) | 🟡 Ready to implement |
| **Track 2: Technique** | Find linear directions for vibrato/falsetto in frozen SSL; steer downstream synthesis | [pro5 §Backup](../../pro_suggestions/pro5_research_direction_ranking.md) | 🟡 Ready to implement |

---

## 📖 How to Read the Design Docs

1. **Start with:** [`design/CODEX_INSTRUCTIONS.md`](design/CODEX_INSTRUCTIONS.md) — the entry point for Codex
2. **Detailed design:** [`../../pro_suggestions/pro3_voice_representation_idea_review.md`](../../pro_suggestions/pro3_voice_representation_idea_review.md) — full Stage A/B/C engineering spec
3. **30-day plan & go/no-go:** [`../../pro_suggestions/pro5_research_direction_ranking.md`](../../pro_suggestions/pro5_research_direction_ranking.md)
4. **Research methodology:** [`../../pro_suggestions/pro7_ml_audio_research_workflow.md`](../../pro_suggestions/pro7_ml_audio_research_workflow.md)

---

## 🖥️ Environment

- **Primary machine:** Lab server (GPU)
- **Reference code:** [`../../arti6_linearvc_demo/`](../../arti6_linearvc_demo/) — `run_timbre_shift_mapper.py`, `run_seedvc_svc_demo.py`
- **Branch:** `codex/research-system-architecture`
