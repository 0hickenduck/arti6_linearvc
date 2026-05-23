# Demo Version 1: ARTI-6 LinearVC Experiment

**Date Archived:** 2026-05-22
**Project Phase:** Initial Timbre Factorization Investigation

## Overview
This archive contains the context, PRDs, and research notes from our first major experiment. The goal was to see if we could achieve Voice Conversion by linearly transforming the 6D articulatory features of the ARTI-6 model.

## Conclusion (The Negative Result)
The experiment proved that linear transformations on ARTI-6's content stream are insufficient for full timbre conversion. We discovered that **ARTI-6 strictly factors out timbre into the Speaker Embedding**, meaning any linear change to the articulatory features only changes pronunciation/accent, not the core vocal identity (timbre leakage).

This insight led to the pivot in Version 2: explicitly steering the Speaker Embedding (Latent Space Steering) or training a micro-mapper for cross-domain timbre shift.

## Contents
* `context/05-18-experiment_prd.md`: The original PRD for running the linear floor experiment.
* `context/05-19-packaging_prd.md`: The PRD for packaging the results and evaluating the failure.
* `context/decision_stop_negative_result_mainline.md`: The decision to stop trying to force ARTI-6 to work via linear transforms.
* `context/positive_direction_shortlist.md`: The 5 alternative research directions generated after the negative result.
* `context/brainstorming_minutes.md`: The meeting minutes capturing the user's insights on cross-domain timbre shift, which serves as the bridge to Version 2.

*Note: The generated audio outputs remain in `outputs/linearvc_floor/` and the packaged demo site remains in `archive/generated_site/`.*