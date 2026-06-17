# Small-GPU Singing Skill Experiment Shortlist

## 1. Technique and Attribute Probe

- Data: VocalSet, GTSinger, optional SVQTD.
- Task: classify vocal techniques and pedagogy attributes.
- Model: frozen SSL/MuQ/BEATs embeddings plus shallow MLP or logistic head; add
  F0/vibrato/energy features.
- Splits: singer-disjoint.
- Metrics: macro-F1, UAR, class-wise recall, confusion matrix.
- Compute: precompute embeddings, train on CPU or one 8-12 GB GPU.
- Gate: good first experiment because VocalSet and GTSinger have accessible data
  and labels.

## 2. No-Reference Current-Quality Baseline

- Data: SingMOS-Pro, SingMOS-v1, optional VocalVerse or SingEval if access is
  settled.
- Task: predict MOS/rank for current perceived singing quality.
- Model: released SingMOS predictor; frozen embeddings plus ridge/MLP; optional
  pitch/energy/vibrato statistics.
- Splits: system-disjoint for SingMOS-Pro; singer/song-disjoint for real-user
  data.
- Metrics: MSE, MAE, Pearson, Spearman, Kendall tau, calibration.
- Compute: released predictor plus shallow heads, single GPU sufficient.
- Gate: use as a quality baseline, not as a claim about future professional
  outcomes.

## 3. Pairwise Improvement and Feedback

- Data: Lyra-SA, PESnQ/SingEval/AME430 if accessible, or a small repeated-take
  pilot.
- Task: pairwise preference/ranking between takes and dimension-level feedback.
- Model: reference pitch/rhythm alignment features plus technique embeddings;
  RankNet/logistic pairwise head.
- Splits: singer-disjoint and song-disjoint where possible.
- Metrics: pairwise accuracy, Spearman/Kendall, feedback usefulness ratings.
- Compute: feature extraction plus shallow ranking model.
- Gate: best formulation for "improvement potential" without unsupported
  longitudinal claims.
