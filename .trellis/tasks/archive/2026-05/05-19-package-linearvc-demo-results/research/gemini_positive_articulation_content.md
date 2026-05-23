# Positive Uses for Articulatory/Content Features (ARTI-6)

Given the negative result for ARTI as a timbre/voice conversion stream, we pivot to exploring its strengths. ARTI appears highly effective as a **phonetic/articulatory content stream**. The following 5 project directions leverage the unique properties of articulatory coding—interpretability, structural preservation, and disentanglement from speaker identity.

## 1. Cross-Lingual Accent Conversion (L2 Pronunciation Correction)
* **Core Claim:** Articulatory representations decouple phonetic intent from speaker timbre better than semantic tokens (e.g., HuBERT). This allows for targeted, localized correction of mispronounced phonemes without altering the speaker's vocal identity.
* **Why it might be novel/useful:** Most accent conversion uses complex disentanglement on latent spaces that are hard to control and often leak speaker identity. Direct articulatory manipulation is interpretable and allows for surgical edits (e.g., adjusting just the 'r'/'l' trajectory).
* **Minimal Experiment:** Extract ARTI-6 features from an L2 English speaker. Identify a mispronounced phoneme, linearly interpolate its articulatory trajectory towards an L1 reference trajectory, and resynthesize using a frozen ARTI-to-Mel decoder.
* **Data Needed:** Parallel or non-parallel L1/L2 speech datasets (e.g., [L2-ARCTIC](https://psi.engr.tamu.edu/l2-arctic-corpus/)).
* **Objective + Listening Eval:** 
  * *Objective:* Word Error Rate (WER) reduction via ASR; Speaker Verification Cosine Similarity (to ensure timbre preservation).
  * *Subjective:* Mean Opinion Score (MOS) for Native-ness and MOS for Speaker Similarity.
* **Failure Mode:** The resynthesis decoder may fail to produce natural audio when fed "hybrid" out-of-distribution articulatory trajectories.
* **Paper or Demo:** High potential for a paper, accompanied by an interactive demo.

## 2. Interpretable Local Speech Editing (Vowel/Formant Tweaking)
* **Core Claim:** ARTI-6 provides a continuous, interpretable manifold for manipulating specific speech characteristics (e.g., vowel height, backness, emphasis) locally, which discrete semantic tokens cannot offer.
* **Why it might be novel/useful:** Traditional speech editing relies on text replacement (requiring full resynthesis and breaking prosody) or latent-space walking (unpredictable). Articulatory editing enables "Photoshop for speech," allowing smooth, localized, continuous tweaks.
* **Minimal Experiment:** Build a UI exposing ARTI-6 dimensions. Take a source utterance, manually offset specific articulatory channels over a 500ms window, and synthesize to observe targeted acoustic changes (e.g., shifting /ae/ to /eh/).
* **Data Needed:** High-quality single-speaker TTS dataset (e.g., [VCTK](https://datashare.ed.ac.uk/handle/10283/2950) or [LJSpeech](https://keithito.com/LJ-Speech-Dataset/)) to train the decoder.
* **Objective + Listening Eval:**
  * *Objective:* Formant tracking (F1/F2 shift correlation with the edit).
  * *Subjective:* ABX preference test comparing the naturalness of the ARTI edit vs. standard pitch/formant shifting DSP algorithms.
* **Failure Mode:** If ARTI dimensions are highly entangled or lack true physical grounding, a single-channel tweak might cause catastrophic artifacts rather than a clean phonetic shift.
* **Paper or Demo:** Primarily a compelling interactive Demo.

## 3. Zero-Shot Intelligibility Enhancement for Dysarthric Speech
* **Core Claim:** ARTI models capture intended articulatory gestures even when acoustic realization is compromised. It can serve as a robust intermediate representation for reconstructing intelligible speech for individuals with dysarthria.
* **Why it might be novel/useful:** Standard ASR-TTS pipelines fail on atypical speech due to text bottlenecks and loss of original prosody. Mapping dysarthric audio to ARTI, correcting the trajectories, and resynthesizing bypasses text and retains better flow.
* **Minimal Experiment:** Train a lightweight seq2seq mapping from dysarthric ARTI trajectories to healthy ARTI trajectories. Resynthesize using a healthy voice decoder.
* **Data Needed:** Dysarthric speech datasets with aligned healthy references (e.g., [TORGO](http://www.cs.toronto.edu/~compling/Research/Dysarthria/) or [UASpeech](http://www.isle.illinois.edu/sst/data/UASpeech/)).
* **Objective + Listening Eval:**
  * *Objective:* ASR WER reduction on the synthesized output.
  * *Subjective:* Intelligibility MOS and Naturalness MOS by human raters.
* **Failure Mode:** The initial ARTI extractor, trained on healthy speech, might fail completely on dysarthric acoustics, outputting noise rather than recoverable intended trajectories.
* **Paper or Demo:** Strong paper potential in the accessibility domain.

## 4. Audio-Driven 3D Facial Animation (Audio2Face) using ARTI
* **Core Claim:** Using ARTI as an intermediate bottleneck for Audio-to-3D-Face generation yields more accurate and generalizing lip-sync than mapping directly from Mel-spectrograms or Wav2Vec2/HuBERT.
* **Why it might be novel/useful:** Facial animation is fundamentally about physical articulation. Explicitly using an articulatory representation bridges the acoustic and visual domains natively, reducing the need for massive paired audio-visual datasets.
* **Minimal Experiment:** Train a simple MLP/Transformer to map ARTI-6 trajectories to 3D facial blendshapes. Compare the lip vertex error against a baseline mapping directly from HuBERT.
* **Data Needed:** Audio-visual datasets with 3D facial tracking (e.g., [VOCASET](https://voca.is.tue.mpg.de/) or [BIWI](https://data.vision.ee.ethz.ch/cvl/datasets/b3faces/)).
* **Objective + Listening Eval:**
  * *Objective:* Lip Vertex Error (LVE) and facial landmark distance.
  * *Subjective:* Visual Naturalness and Audio-Visual Synchronization MOS.
* **Failure Mode:** ARTI-6 might strip away acoustic information (like volume or global energy) that dictates non-lip facial movements (e.g., jaw dropping for loud speech, eyebrow movement).
* **Paper or Demo:** Can be both; highly visual demo and a solid methodology paper.

## 5. Disentangled Emotional Prosody Transfer
* **Core Claim:** By explicitly separating speech into ARTI (content), F0 (pitch), and Timbre, we can perform highly accurate emotional prosody transfer by transplanting F0 and altering speaking rate while keeping the ARTI content strictly preserved.
* **Why it might be novel/useful:** Emotional voice conversion often inadvertently changes phonetic content or speaker identity because extreme emotions heavily warp acoustics. ARTI's strong content preservation ensures intense emotional prosody doesn't destroy the underlying words.
* **Minimal Experiment:** Extract ARTI, F0, and speaker embeddings from a neutral source and an emotional target. Combine source ARTI + source speaker embedding + target F0. Use a duration predictor to warp the ARTI sequence to match the target's rhythm.
* **Data Needed:** Emotional Speech Datasets (e.g., [ESD](https://hltsingapore.github.io/ESD/) or [RAVDESS](https://zenodo.org/record/1188976)).
* **Objective + Listening Eval:**
  * *Objective:* F0 correlation with the target; WER (to ensure content preservation).
  * *Subjective:* Emotion Similarity MOS and Speaker Similarity MOS.
* **Failure Mode:** Emotion also affects physical articulation (e.g., a "smile" changes lip spreading and formants). Keeping ARTI strictly neutral might result in the emotion sounding artificial or disconnected from the mouth shape.
* **Paper or Demo:** Strong demo, potential paper if the disentanglement significantly outperforms latent-based baselines.