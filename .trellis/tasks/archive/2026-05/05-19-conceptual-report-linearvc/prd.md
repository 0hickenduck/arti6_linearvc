# Conceptual Report: ARTI-6 and LinearVC

## Goal

Create a comprehensive conceptual report explaining the ARTI-6 model and the LinearVC approach. The report should bridge the gap between high-level intuition (using analogies) and technical implementation details, providing a roadmap for current work and future directions.

## What I already know

* **ARTI-6**: A representation learning model focused on articulation. It captures the physical/muscular aspects of speech.
* **LinearVC**: A voice conversion method that uses a linear transformation (matrix) to shift embeddings from one speaker's space to another, rather than replacing speaker embeddings.
* **Current State**: We are exploring the "floor" of this approach (minimal/baseline performance) and visualizing results.
* **Target Audience**: The user (bowen), looking for both big-picture understanding and technical rigor.

## Assumptions (temporary)

* The user wants the report in Markdown format.
* The report should include the "Musical Instrument" analogy discussed in the chat.
* Socratic questions should be embedded or addressed in the report.

## Open Questions

* Are there specific technical metrics or experiment results from `arti6_linearvc_demo` that should be explicitly detailed in this report?
* Should the report include a "Roadmap" section for the next steps of the `arti6_linearvc` project?

## Requirements (evolving)

* **Intuitive Explanation**: Use the "Pianist and Piano" analogy. ARTI-6 = Finger movements (Technique); Speaker Embedding = The Piano itself (Instrument).
* **Technical Detail**: 
    * Explain the 6 audio conditions in the "Floor" experiment:
        1. **Source Reconstruction**: Source Articulation + Source ID (The original performance).
        2. **Target Reconstruction**: Target Articulation + Target ID (The goal sound).
        3. **Embedding-only VC**: Source Articulation + Target ID (Changing the piano, but not the technique).
        4. **Mean/Std VC**: Adjusted Source Articulation (Mean/Std shift) + Target ID.
        5. **Diagonal Affine VC**: Adjusted Source Articulation (per-dim Scale/Bias) + Target ID.
        6. **Full Affine VC**: Adjusted Source Articulation (6x6 Matrix) + Target ID.
    * Explain the linear transformation $y = Wx + b$ as a way to "calibrate" the articulation movement for a new speaker's physical constraints.
* **ARTI-6 Role**: Explain why articulation is the chosen representation: it's physical, interpretable, and captures nuances (timbre, effort) that tokens/phonemes lose.
* **LinearVC Role**: Explain why a linear transformation is used: it tests the hypothesis that speaker differences in articulation are largely structural/affine.

## Acceptance Criteria (evolving)

* [ ] Report file `conceptual_report.md` created in the task directory.
* [ ] The 6 "Floor" conditions are clearly defined and linked to the philosophy.
* [ ] Socratic questions are included to provoke deeper thought.
* [ ] The distinction between "Source" and "Target" speaker roles is clarified.

## Definition of Done

* Report written, reviewed, and persisted.
* User understands the 6 demo audios and the underlying "Piano" philosophy.

## Out of Scope

* Detailed mathematical proofs or code implementation.

## Technical Notes

* **ARTI-6 Features**: 6D articulatory trajectories (LA, TT, TB, VL, TR, LX).
* **Speaker Embedding**: 192D x-vector style embedding.
* **Transformation Logic**: $y = Wx + b$ where $x$ is 6D source articulation and $y$ is the predicted target articulation.
* Related files: `arti6_linearvc_demo/run_linearvc_floor.py`.
