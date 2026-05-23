# Research: Latent Steering and Embedding "Sliders"

- **Query**: Latent space steering methods in Deep Learning, "sliders" in embedding spaces, related work in CV (StyleGAN) and Speech, and novelty for a Master's student.
- **Scope**: Mixed (External Research + Internal Context)
- **Date**: 2025-05-22

## Findings

### How "Sliders" are Found

In generative models, a "slider" corresponds to a **steering vector** $v$ in the latent space $Z$ (or $W$). Moving the slider adjusts the output by adding a scaled version of this vector: $z' = z + \alpha v$. Finding these vectors can be done via supervised or unsupervised methods.

#### 1. Unsupervised Methods (Automatic Discovery)
*   **PCA (Principal Component Analysis)**: The simplest approach. Sampling many latent codes and finding the directions of highest variance often reveals major semantic traits (e.g., pose in images, pitch in speech).
*   **GANSpace**: Applies PCA to the activations of specific layers. It discovered that different layers control different levels of detail (coarse vs. fine), leading to "layer-wise" steering.
*   **SeFa (Semantic Factorization)**: A "closed-form" method that analyzes the **weights** of the generator directly without sampling data. It finds directions that the model is mathematically "primed" to represent.

#### 2. Supervised Methods (Targeted Control)
*   **InterFaceGAN**: Requires a labeled dataset (e.g., "smiling" vs. "neutral"). A linear SVM is trained in the latent space to find the separating hyperplane. The normal vector to this plane becomes the steering vector.

---

### Related Work: Computer Vision vs. Speech

| Domain | Key Models | Typical "Sliders" |
| :--- | :--- | :--- |
| **Computer Vision** | StyleGAN (1/2/3), BigGAN | Age, Gender, Smile, Lighting, Pose, Glasses. |
| **Speech** | RAVE, So-VITS-SVC, SpeechSplit, EmoSteer-TTS | Pitch ($F_0$), Timbre identity, Breathiness, Nasality, Emotional Intensity. |

**Key Difference**: Speech requires preserving temporal coherence and phonetics (content) while steering style (timbre/prosody). In images, spatial coherence is the equivalent, but speech is 1D and highly sensitive to phase and local artifacts.

---

### Novelty for a Master's Student in Speech

For a Master's level project (specifically in the context of `LinearVC` or `arti6`), the following areas represent significant novelty and research potential:

1.  **Unsupervised Discovery of Speech Semantics**: Applying **SeFa** or **GANSpace** to audio autoencoders (like WavLM-based decoders) to find "natural" sliders for traits like *vocal fry, breathiness,* or *nasality* without needing labeled datasets.
2.  **Addressing Attribute Leakage**: A major problem in speech steering is that changing "pitch" often accidentally changes "timbre" (the chipmunk effect). Developing methods that ensure **orthogonality** (true disentanglement) is a high-value contribution.
3.  **Training-Free Control**: Most VC models require fine-tuning. Researching "post-hoc" steering vectors that work on top of frozen, pre-trained models (like F5-TTS or Hubert) allows for "plug-and-play" voice modification.
4.  **Steering Metrics**: Developing new metrics to measure **Steering Efficiency** (how much the trait changed) vs. **Preservation Integrity** (how well the identity and content were kept).
5.  **Layer-Wise Interpretability**: Mapping which layers of a speech decoder (e.g., HiFi-GAN or BigVGAN) control specific acoustic features.

### Related Specs
- `.trellis/spec/arti6-linearvc-acceptance.md` — Defines the quality gates for steering results.

## Caveats / Not Found
*   **Non-linear Steering**: Most current research assumes steering is a linear addition. There is very little work on "curved" steering paths in speech latent spaces, which might be necessary for more complex emotional transitions.
*   **Cross-Speaker Stability**: A vector found for one speaker often fails to produce the same effect on another speaker. This "generalization gap" is a known difficult problem.
