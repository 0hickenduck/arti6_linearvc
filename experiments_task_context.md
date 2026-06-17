# Experiment Implementation Task Context

**Objective:** Implement the two parallel research tracks (Timbre Mode Residual & Technique Probing) as outlined in the project blueprint. This document provides the necessary context, design constraints, and task breakdown for the coding agent to execute.

## 1. Required Context Reading
Before writing any code, the agent MUST read and understand the following design documents:

* **Master Blueprint:** [project_blueprint_tracks.md](file:///Users/bowen/research/project/free_recall/project_blueprint_tracks.md) - Contains the exact definitions of Track 1 (Timbre) and Track 2 (Technique).
* **Methodologies & Math:** [nuisance_control_methodologies.md](file:///Users/bowen/research/project/free_recall/nuisance_control_methodologies.md) - Contains the math for residualization, Gradient Reversal Layer (GRL), and the "Golden Rule of Conditioning" (FiLM vs. Cross-Attention).
* **Architecture Background:** [latent_space_architecture_free_recall.md](file:///Users/bowen/research/project/free_recall/latent_space_architecture_free_recall.md)

## 2. Reference Code
Review these existing files to understand the current implementation state:
* [run_timbre_shift_mapper.py](file:///Users/bowen/research/project/arti6_linearvc_demo/run_timbre_shift_mapper.py) - Contains the `MicroMapper` class (Residual MLP) and basic training setup.
* [run_seedvc_svc_demo.py](file:///Users/bowen/research/project/arti6_linearvc_demo/run_seedvc_svc_demo.py) - Contains inference logic for injecting embeddings into the frozen Seed-VC decoder.

## 3. Tasks Breakdown

### Track 1: Timbre Shift (Mode Residual Mapper)
1. **Data Preparation Script:** Write a script to iterate over a paired speech-to-singing dataset (e.g., JVS-MuSiC).
   * Extract the speaking voice array and singing voice array for each speaker.
   * Pass them through the **frozen Seed-VC speaker encoder** to yield disentangled $T_{\text{speech}}$ and $T_{\text{singing}}$ vectors.
   * Save the paired embeddings to a robust format (e.g., NumPy `.npy` arrays or a PyTorch dataset).
2. **MicroMapper Training:** Update the existing `run_timbre_shift_mapper.py` to ingest the extracted dataset.
   * Train the `MicroMapper` (MLP) to map $T_{\text{speech}} \to T_{\text{singing}}$.
   * Ensure the loss function (Cosine Similarity / MSE) properly converges.
3. **Integration & Inference:** Connect the trained MicroMapper output to the injection point in `run_seedvc_svc_demo.py` so that a user's speech embedding can dynamically prompt the singing generator.

### Track 2: Technique Probing & Reconstruction
1. **Analogy Probing Script (Stage A):**
   * Load GTSinger phone-level technique labels.
   * Extract frame-level features for the *same* phoneme under *different* techniques (e.g., Normal vs. Vibrato).
   * Load 4 foundation models: WavLM, HuBERT, ContentVec, MERT.
   * Calculate $\Delta Z = Z_{\text{vibrato}} - Z_{\text{normal}}$ and perform bootstrapping to measure the stability (variance) of this linear direction in each model's latent space.
2. **Reconstruction Pipeline (Stage B/C):**
   * Implement **Latent Steering**: $Z_{\text{new}} = Z + \Delta Z$ and feed to a downstream frozen decoder.
   * *Alternative/Extension:* Implement LoRA matrices combined with a Gradient Reversal Layer (GRL) on the base model to strip technique information from the content branch.

## 4. Design Guidelines for Codex
* **Keep Decoders Frozen:** Do not perform end-to-end training of the massive synthesizer models. We are training lightweight adapters (MicroMapper) and utilizing parameter-efficient techniques.
* **Modularity:** Ensure the data extraction logic is decoupled from the training loops.
* **Logging:** Print shapes of tensors explicitly during development to avoid dimension mismatch errors (e.g., `(Batch, Time, Channels)`).
