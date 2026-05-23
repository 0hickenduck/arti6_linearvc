# Research Directions Overview: Finding a New Path for ARTI-6

*Date: 2026-05-22*

This document provides a high-level overview of the five research directions proposed after the initial ARTI-6 experiment (which showed that trying to linearly change voice timbre using just articulatory content doesn't work well). 

Think of voice synthesis like **directing a play**. You have the **Script & Actor's Movements** (the phonetic/articulatory content) and you have the **Costumes & Lighting** (the timbre/speaker identity). Our previous experiment tried to change the costumes by tweaking the script—which naturally failed. 

Here are five new ways we can approach the problem, along with intuitive analogies:

---

## 1. Speaker Embedding Steering inside ARTI-6
**The Analogy: The "Costume Department" Slider**
Instead of changing the script, we go straight to the costume department (the Speaker Embedding path). Imagine having a slider that blends a "male costume" and a "female costume," or a "husky voice" and a "clear voice." 
* **Position in the field:** This falls under **Latent Space Manipulation**. It’s very popular right now because you reuse a powerful AI model's built-in understanding of identity without retraining it.
* **Why it matters:** It's cheap, fast, and directly uses what ARTI-6 is already good at (separating content from speaker ID).

## 2. Source-Filter Physical Timbre Knobs (WORLD, VTLN, McAdams)
**The Analogy: The "Audio Equalizer" on Steroids**
Instead of using AI to imagine a new voice, we use classical physics. Imagine taking a recorded voice and physically stretching the virtual vocal cords (making them longer for a deeper resonance, like a cello vs. a violin) or shifting the pitch. 
* **Position in the field:** This is **Classical Digital Signal Processing (DSP)**. It’s highly interpretable—we know exactly *why* the audio changes, unlike black-box AI.
* **Why it matters:** It gives immediate, guaranteed results. It might sound a bit robotic ("classical" artifacts), but it provides a rock-solid baseline for what a "tweakable" voice should be.

## 3. SSL-Space Small Method (Delta-VC, Locally linear kNN-VC)
**The Analogy: The "Collage Artist"**
Imagine you have a massive magazine (WavLM features) filled with tiny snippets of speech. To make a new voice, you cut out snippets that match the content you want but belong to the target speaker. We would try to make this cutting-and-pasting smoother (like using better glue or finding better matching snippets).
* **Position in the field:** This is **Self-Supervised Learning (SSL) Voice Conversion**. It's the current state-of-the-art for any-to-any voice conversion (like kNN-VC).i
* **Why it matters:** It moves away from ARTI-6 completely and tries to slightly improve the reignng champion method. It's safer but runs the risk of being "just another minor tweak" unless it sounds significantly better.

## 4. ARTI for Accent / Pronunciation Editing
**The Analogy: The "Dialect Coach"**
Instead of trying to change *who* is speaking (timbre), we use ARTI-6 for what it does best: changing *how* they speak (articulation). Imagine leaving the actor's costume alone but hiring a dialect coach to fix their accent.
* **Position in the field:** This is **Pronunciation/Accent Conversion**. It is a niche but highly valuable area, especially for language learning and localization.
* **Why it matters:** It plays directly to the strengths of the 6D articulatory features. However, evaluating it requires specific datasets and human listening tests.

## 5. Dynamic Speaker Embeddings
**The Analogy: The "Chameleon Costume"**
Currently, an AI voice uses one static "costume" for the whole sentence. But human voices change constantly—we get raspy, we laugh, we sigh. This direction proposes updating the costume every millisecond based on what's happening in the audio.
* **Position in the field:** This addresses **Expressive/Fine-grained Voice Conversion**. 
* **Why it matters:** It's a great concept, but technically very risky because the current ARTI-6 model might break if you try to change its costume mid-sentence.

---

### Socratic Discussion Checkpoint

Before we dive deep into the technical implementation of any of these, let's look at the big picture. 
Our constraints are: we want something that doesn't require massive retraining, and gives us a good demo or paper quickly.

Looking at the **Costume Slider (1)** and the **Audio Equalizer (2)**:
* One uses the AI's internal "brain" to guess what a voice should sound like.
* The other uses hard physics and math to stretch the audio waves.

**Question for you:** When you think about the final demo or the story you want to tell in your research, do you prefer a story about *discovering hidden controls inside an AI* (Direction 1), or a story about *combining modern AI content with classical, interpretable physical controls* (Direction 2)? 
