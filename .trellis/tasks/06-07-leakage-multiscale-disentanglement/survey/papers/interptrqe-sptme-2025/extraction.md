# InterpTRQE-SptME / InterpTF-SptME (2025)

## Idea

SSL content embeddings retain speaker information. SHAP-based interpretability
can quantify residual speaker information and guide post-hoc filtering.

## Method

The benchmark extracts content embeddings from SSL models and speaker embeddings
from ECAPA-TDNN, trains a speaker classifier, and uses Gradient SHAP to estimate
what proportion of the classifier decision comes from content dimensions.
Filtering adds SHAP-scaled noise or suppresses speaker-contributing dimensions.

## Experiment Design

Experiments evaluate seven SSL/pretrained models on VCTK. The paper measures
timbre residual ratio, ASR CTC loss for content preservation, and stability.

## Datasets and Metrics

VCTK with 20 speakers and 7,758 utterances. Models include HuBERT, WavLM,
ContentVec, DPHuBERT, Whisper-ppg, and HuBERT-CH. Metrics include timbre
residual percentage and CTC loss.

## Ablations

Reported comparisons include model/layer residuals and filtering tradeoffs. The
paper reports HuBERT Large layer 21 dropping from 18.65% residual to near zero
or low residual under SHAP noise at modest CTC loss cost.

## Code Availability

The paper lists a GitHub repository. It was not cloned or run in this survey, so
use it as citation evidence unless local install succeeds later.

## Relevance

This paper is the closest leakage-audit risk. A probe-only version of the
current project will look incremental unless it adds speech/singing mode,
temporal bands, phonetic/F0 controls, and downstream causal intervention.

Sources: https://arxiv.org/abs/2507.17851,
https://github.com/zhuxiaoxuhit/InterpTRQE-SptME

