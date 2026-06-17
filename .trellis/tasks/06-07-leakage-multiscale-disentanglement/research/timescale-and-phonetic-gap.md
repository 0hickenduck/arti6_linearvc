# Temporal Scales, F0, and the Phonetic Identity Gap

Research cutoff: 2026-06-07.

## Are 50--100 ms bands used?

Yes, but papers use "scale" in three different ways:

1. token/frame resolution;
2. an integration or smoothing window;
3. a temporal modulation-frequency band.

These are not equivalent.

Examples:

- CoFi-Speech uses 20, 40, and 120 ms codec token resolutions. The choices
  mainly balance sequence length, detail, and coarse-to-fine language-model
  behavior; the paper does not demonstrate that each scale is a pure
  linguistic factor.
- MsCodec uses hierarchical stride-two resolutions, producing configurations
  in approximately the 6.25--100 ms range. Its choices come mainly from
  architecture and bitrate constraints.
- LoIN studies local versus global mean/std statistics, but does not define a
  linguistically pure 50--100 ms band.
- Speech rhythm research often uses modulation rates instead: roughly
  4--10 Hz for faster phone/syllable-related changes and 0.5--4 Hz for slower
  prosodic-group structure.

## Why those ranges are plausible

Speech science provides approximate priors:

- spectral analysis frames: about 10--25 ms;
- local phonetic cues and transitions: tens of milliseconds;
- phoneme durations: often about 30--150 ms;
- syllabic organization: often about 100--300 ms;
- phrase prosody: hundreds of milliseconds to seconds.

These distributions overlap and change with language, rate, phone class,
coarticulation, singer, technique, and note duration. Consequently, a paper
should not pre-label `<100 ms` as "phonetic." A defensible design uses these
ranges to choose a search grid and then validates their information content.

## Is a short band merely degraded F0?

No.

F0 is vocal-fold carrier periodicity, commonly around 80--400+ Hz, with periods
of roughly 2.5--12.5 ms. A 50--100 ms window spans several pitch periods and
can estimate F0, but it also contains:

- formant transitions;
- consonant bursts and voice onset time;
- phone boundaries and coarticulation;
- energy and voicing changes;
- local spectral-envelope and speaker cues.

A temporal modulation rate, such as 10 Hz, describes how a contour, envelope,
or latent feature changes. It is not the F0 value.

F0 remains a major confound. Singing vibrato and pitch transitions can dominate
mid-scale bands. Therefore repeat scale results with:

1. raw data;
2. F0-matched sampling;
3. F0-regressed representation residuals;
4. explicit F0 and voicing probes.

If an apparent vocal-mode effect vanishes after F0 control, it was mainly
pitch-mediated rather than evidence of independent mode information.

## Why hard linguistic bands are uncommon

- Phone and syllable durations overlap.
- Speaking and singing rates vary.
- Coarticulation crosses phone boundaries.
- Encoder receptive fields already mix temporal contexts.
- Hard filters introduce arbitrary boundary behavior.
- Codec papers are usually optimizing bitrate and reconstruction rather than
  validating linguistic purity.

The experiment should therefore sweep logarithmic durations and compare them
with phone- or syllable-aligned pooling.

## Phonetic identity gap

Speaker embeddings retain phonetic information. Prior work reports:

- phonetic mismatch between enrollment and test degrades speaker verification;
- frame-level phonetic supervision can improve speaker modeling;
- phonetic information in the final utterance embedding can behave as nuisance
  variability;
- same-phone trials can outperform duration-matched random speech;
- phone-specific speaker cues vary across speakers.

Thus the observed speech/singing identity gap can partly reflect different
phone inventories and realizations, not only a change in vocal identity.

Required comparisons:

1. same speaker, same phone, speech versus singing;
2. same speaker, different phone, same mode;
3. same speaker, different phone, different mode;
4. different speaker, same phone.

Begin with aligned vowel interiors, then compare consonant classes, diphone
transitions, and phone-center versus phone-boundary frames. Control duration,
mean/range F0, SNR, song, and speaker with a mixed-effects model.

## Recommended scale sweep

Use:

```text
20, 40, 80, 160, 320, 640, 1280 ms
```

alongside:

- temporal modulation filters;
- phone-center pooling;
- phone-boundary windows;
- duration-normalized phone trajectories;
- syllable/note-aligned pooling.

Select scales using validation singers. Only attach linguistic interpretations
after measuring phone, F0, mode, and identity accessibility.

## Sources

- [CoFi-Speech](https://arxiv.org/abs/2409.11630)
- [MsCodec](https://arxiv.org/abs/2410.15749)
- [LoIN](https://www.isca-archive.org/interspeech_2023/gu23b_interspeech.html)
- [Temporal speech-processing review](https://pmc.ncbi.nlm.nih.gov/articles/PMC3364513/)
- [Short temporal integration in vowel perception](https://pmc.ncbi.nlm.nih.gov/articles/PMC2677283/)
- [Phonetic information in speaker embeddings](https://www.isca-archive.org/interspeech_2019/wang19d_interspeech.html)
- [Phonetic analysis of speaker verification](https://www.isca-archive.org/odyssey_2024/thebaud24_odyssey.html)

