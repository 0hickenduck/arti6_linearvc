# SSL-Space Voice Conversion: Novel Project Ideas (Beyond Simple Reproduction)

This document proposes 5 concrete voice conversion (VC) project ideas focused on Self-Supervised Learning (SSL) representations. The ideas center on retrieval, linear algebra, and lightweight adaptation, avoiding simple reproductions of ARTI-only LinearVC or baseline kNN-VC.

## 1. Locally Linear kNN-VC (LL-VC): Continuous Phonetic Manifold Interpolation
*   **Core Claim:** Standard kNN-VC suffers from discrete retrieval artifacts (clicking or jitter) because it strictly selects or averages the nearest $k$ discrete frames from the target. By treating the target frames as a local manifold and using Locally Linear Embedding (LLE) or barycentric coordinates, we can continuously synthesize a *new* target frame that perfectly matches the source's phonetic geometry.
*   **Novelty:** Replaces discrete vector quantization / kNN with continuous linear algebraic manifold interpolation. It bridges the gap between retrieval and generation without neural network training.
*   **Minimal Experiment:** Extract WavLM representations of a source utterance and a target reference. For each source frame, retrieve the top $K$ nearest target frames. Solve a small constrained least-squares problem (weights summing to 1) to reconstruct the source frame, then use those weights to interpolate the target frames. Pass the interpolated frames to a pre-trained HiFi-GAN vocoder.
*   **Data Needed:** Zero-shot. Needs only one target speaker utterance (3-10 seconds) and a standard pretrained SSL vocoder (e.g., from the kNN-VC repo).
*   **Evaluation:** Mel-cepstral distortion (MCD) for acoustic fidelity, Word Error Rate (WER) via Whisper for intelligibility, and Speaker Similarity MOS (SMOS).
*   **Failure Mode:** If the target reference is too short, the local manifold is sparse, and least-squares interpolation might yield a vector near the origin (oversmoothing), resulting in muffled or buzzy audio.
*   **Paper/Demo Potential:** High potential for a short ICASSP/Interspeech paper or a viral web demo. It's a mathematically elegant, drop-in replacement for kNN-VC that should yield visibly smoother pitch and spectral transitions.
*   **Relevant URLs:** kNN-VC base ([arXiv:2305.18975](https://arxiv.org/abs/2305.18975)), Locally Linear Embedding ([Science](https://www.science.org/doi/10.1126/science.290.5500.2323)).

## 2. Singular Value Subspace Projection VC (SVD-VC)
*   **Core Claim:** Speaker identity in SSL space (like WavLM Layer 6) is largely linearly separable and occupies a low-dimensional subspace orthogonal to phonetic content. We can perform VC purely via matrix projection.
*   **Novelty:** Zero-shot, non-parametric, and extremely fast. It operates on the hypothesis that speaker traits can be isolated via SVD on the covariance matrix of a speaker's SSL features, removing the need for frame-by-frame retrieval.
*   **Minimal Experiment:** Compute the SVD of the target speaker's feature matrix $T$. Identify the top $N$ principal components spanning the "target speaker subspace." Project the source feature matrix $S$ into this subspace (e.g., $S' = S \cdot V_N \cdot V_N^T$, potentially subtracting the source's own principal components first).
*   **Data Needed:** Zero-shot. 5 seconds of source audio, 5-10 seconds of target audio.
*   **Evaluation:** Cosine similarity of Resemblyzer/WavLM speaker embeddings (objective) and subjective ABX tests.
*   **Failure Mode:** *Critical overclaiming risk:* SVD might mostly capture phonetic variance (vowels vs. consonants) in its top components rather than static speaker traits. If true, the projection will corrupt the phonetics and leave the speaker identity untouched.
*   **Paper/Demo Potential:** "Speaker Identity as a Linear Subspace in WavLM". Good for a workshop paper (e.g., NeurIPS SSL workshop). If it works, it's computationally trivial and highly demo-able.

## 3. Optimal Transport VC (OT-VC) for Global Feature Mapping
*   **Core Claim:** kNN-VC makes greedy, local decisions frame-by-frame, often mapping many source frames to the *same* target frame (mode collapse), ignoring the global distribution of the target utterance. Optimal Transport (OT) enforces that the entire source distribution maps smoothly to the entire target distribution.
*   **Novelty:** Applies discrete optimal transport (Sinkhorn distances) to SSL feature spaces to find a structurally sound, globally consistent alignment matrix between source and target, rather than independent nearest neighbors.
*   **Minimal Experiment:** Compute the pairwise cosine distance matrix between all source SSL frames and target SSL frames. Use the Sinkhorn-Knopp algorithm to find the optimal transport plan (coupling matrix). Multiply the source features by this coupling matrix to yield the converted features.
*   **Data Needed:** Zero-shot. Needs utterances of similar lengths for best results.
*   **Evaluation:** Fréchet Audio Distance (FAD) to measure distribution similarity, F0 correlation.
*   **Failure Mode:** If the source says "Hello" (short, vowels) and the target reference is "The quick brown fox" (long, diverse), the global OT constraint will force the "Hello" frames to map to irrelevant consonants in the target, destroying intelligibility.
*   **Paper/Demo Potential:** Solid theoretical grounding. Fits well into ML conferences (ICLR/NeurIPS) due to the OT angle. 
*   **Relevant URLs:** Optimal Transport for VC (Mel-space) ([arXiv:2104.02456](https://arxiv.org/abs/2104.02456)), Sinkhorn Algorithm.

## 4. Feature-Space Shift / Task-Arithmetic VC ($\Delta$-VC)
*   **Core Claim:** Similar to word2vec ($King - Man + Woman = Queen$) or LLM task arithmetic, speaker identity in deep SSL layers can be modified by adding a simple global offset vector: $Z_{converted} = Z_{source} - \mu_{source} + \mu_{target}$.
*   **Novelty:** The absolute simplest adaptation possible. It tests the linearity of disentanglement in modern SSL models (like HuBERT/WavLM).
*   **Minimal Experiment:** Compute the mean WavLM vector across several utterances for Speaker A ($\mu_A$) and Speaker B ($\mu_B$). For a new utterance from A, compute $Z_{new} = Z_A + (\mu_B - \mu_A)$. Pass $Z_{new}$ to the vocoder.
*   **Data Needed:** ~30 seconds of audio per speaker to compute stable feature means.
*   **Evaluation:** Plotting the trade-off curve between WER (intelligibility degradation) and SMOS as the scalar weight $\alpha$ varies in $Z_{new} = Z_A + \alpha(\mu_B - \mu_A)$.
*   **Failure Mode:** Highly likely that speaker identity is non-linear and entangled with pitch/formants in ways a simple mean shift cannot resolve. The result might just sound like the source speaker with added static noise.
*   **Paper/Demo Potential:** An excellent short analysis paper. Even a negative result ("Why you can't just add a speaker vector in WavLM space") is highly publishable as an analysis of SSL disentanglement.
*   **Relevant URLs:** Editing Models with Task Arithmetic ([arXiv:2212.04089](https://arxiv.org/abs/2212.04089)).

## 5. Parameter-Efficient Cross-Attention Adapter (Light-Adapt-VC)
*   **Core Claim:** Rather than using non-parametric kNN, we can achieve superior any-to-any conversion by freezing the SSL model and the vocoder, and training *only* a single lightweight Cross-Attention layer (an Adapter) to query the target reference frames.
*   **Novelty:** Bridges the gap between entirely non-parametric methods (kNN-VC) and heavy parametric models (FreeVC). It uses the attention mechanism as a trainable, soft-retrieval system.
*   **Minimal Experiment:** Freeze WavLM and a HiFi-GAN. Insert one Multi-Head Cross-Attention layer. The source WavLM features act as Queries, and the target WavLM features act as Keys/Values. Train *only* this attention layer (a few thousand parameters) using a reconstruction loss on a multi-speaker dataset.
*   **Data Needed:** VCTK or LibriTTS (100h) for training the adapter. At inference, just 3 seconds of target audio.
*   **Evaluation:** Inference latency (should be $\mathcal{O}(N \times M)$ but highly parallelizable on GPU compared to CPU-bound exact kNN), model size vs. SMOS.
*   **Failure Mode:** The attention mechanism might collapse into a static average of the target frames, or act as an identity auto-encoder, failing to perform dynamic phonetic alignment.
*   **Paper/Demo Potential:** Very strong "Parameter-Efficient Fine-Tuning" (PEFT) angle for speech. High utility for deployment since it replaces a large exact-match vector index with a tiny, fast neural layer.
*   **Relevant URLs:** FreeVC ([arXiv:2210.15418](https://arxiv.org/abs/2210.15418)), PEFT in Speech ([arXiv:2302.10864](https://arxiv.org/abs/2302.10864)).
