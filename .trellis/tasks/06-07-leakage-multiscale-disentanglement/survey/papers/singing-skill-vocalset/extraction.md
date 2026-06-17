# VocalSet

## Idea

VocalSet is a controlled a cappella singing dataset for vocal technique and singer
identification. It is not a skill-quality dataset, but it is useful for building
technique probes cheaply.

## Method

The original paper trains CNN classifiers in PyTorch for 10 technique labels and
singer identity. It highlights class imbalance and common confusions between
straight tone and vibrato.

## Datasets and Labels

10.1 hours of a cappella recordings from 20 professional singers, 11 male and 9
female, covering 17 techniques, vowels, and melodic contexts. The Zenodo release
includes VocalSet and Annotated VocalSet with manual corrections.

## Metrics and Experiments

Use accuracy, macro-F1, UAR, and confusion matrices. Use singer-disjoint splits
for any generalizable technique detector; random segment splits inflate results.

## Ablations

Useful ablations: technique subset, SSL embedding choice, F0/vibrato summary
features, segment length, and class-balancing strategy.

## Code Availability

Dataset is public on Zenodo. The paper's CNN baseline is simple enough to
reproduce, but a current benchmark should use open embeddings plus a small head
rather than depend on unverified historical code.

## Relevance

Good small-GPU dataset for technique detection experiments. It should not be used
as evidence of overall singing skill or future potential.
