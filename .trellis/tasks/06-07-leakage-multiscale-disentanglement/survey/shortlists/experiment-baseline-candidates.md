# Experiment Baseline Candidates

Date: 2026-06-08.

## Immediate Baselines

1. GTSinger
   - Role: dataset and split backbone.
   - Use: singer-disjoint speech/singing leakage probes, technique classification,
     paired speech/singing residual analysis.
   - Gate: public dataset/code; respect license and avoid language-disentanglement
     claims.

2. Seed-VC
   - Role: downstream conversion baseline and local integration target.
   - Use: compare raw speech prompt, singing prompt, global residual, and learned
     multiscale residual conditioning.
   - Gate: public code/checkpoints and SVC mode.

3. FACodec
   - Role: factorized-codec baseline.
   - Use: content/prosody/timbre/residual leakage probes and stream recombination.
   - Gate: public code/checkpoints; validate on singing because it is speech-centered.

4. Serenade
   - Role: singing style conversion baseline.
   - Use: style/technique leakage and melody preservation comparisons.
   - Gate: public code and GTSinger SSC recipe; noncommercial license.

5. FreeSVC
   - Role: cross-lingual SVC stress-test baseline.
   - Use: evaluate language/content/speaker leakage under multilingual conversion.
   - Gate: public repo/checkpoints; avoid treating this as same-person language
     causality.

## Secondary Baselines

- Vevo1.5/Vevo2 through Amphion/Hugging Face: strong inference baseline for
  unified speech/singing generation, but too large and partly internal-data
  dependent for full reproduction.
- HQ-SVC: useful inference comparison for low-resource zero-shot SVC; training
  code was not public in the checked README.

## Reference Only

- S2Voice: current SVCC 2025 winner and strong style-conditioning reference, but
  no public implementation identified.
- DAFMSVC: relevant leakage-control method through target SSL feature replacement,
  but no public implementation identified.
- R2-SVC: useful robustness threat model for separated-vocal artifacts and noisy
  conditions, but no public implementation identified.
- Singing-to-speech generative flow: useful cross-mode normalization concept, but
  no public implementation identified.
