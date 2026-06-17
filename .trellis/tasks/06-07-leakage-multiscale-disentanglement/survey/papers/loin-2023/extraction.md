# LoIN (2023)

## Idea

Local feature statistics can be used to improve decoupling when instance
normalization with only global statistics is insufficient.

## Method

LoIN calculates local mean/std statistics from randomly selected frames during
training and imposes local/global consistency constraints. It is lightweight and
can be attached to IN-driven VC methods.

## Experiment Design

Voice-conversion experiments compare decoupling, speaker similarity, and content
consistency with and without locality-based statistics.

## Datasets and Metrics

The ISCA abstract reports VC transfer performance, speaker similarity, and
content consistency. It does not evaluate speech/singing identity transfer or
temporal scale bands.

## Ablations

The core ablation is local statistics versus global IN-driven normalization.

## Code Availability

No maintained official implementation was identified in the targeted search.
Survey/reference only by benchmark gate.

## Relevance

LoIN is a direct overlap risk for "local statistics improve disentanglement."
The current project should position its bands as an evaluation map over
speech/singing factors, not as the invention of local statistics.

Source: https://www.isca-archive.org/interspeech_2023/gu23b_interspeech.html

