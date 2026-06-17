## 2026-06-08 - Gemini delegation script missing

- Context: Tried to use AGENTS.md worker-bee delegation for broad local research scouting before survey work.
- Command: `~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh --model flash ...`
- Evidence: zsh: no such file or directory: /Users/bowen/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh
- Next diagnostic: Use native Codex sub-agents for this survey run; later verify whether Gemini extension path moved or is not installed on this machine.

## 2026-06-08 - Gemini survey delegation script missing

- Context: Tried to delegate broad baseline code/checkpoint availability scan for WavLM, ContentVec, FACodec, Seed-VC, kNN-VC, RVC, so-vits-svc, and DDSP-SVC.
- Command: `~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh --model flash --prompt <baseline availability scan>`
- Evidence: zsh returned: no such file or directory: /Users/bowen/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh
- Next diagnostic: Proceed with direct web/source inspection; if delegation is needed later, verify ~/.gemini extension installation path.

## 2026-06-08 - Guessed SingMOS Hugging Face model API paths inaccessible

- Context: Checking whether SingMOS-Pro had a direct Hugging Face model endpoint for pretrained MOS predictor.
- Command: `curl -L -s https://huggingface.co/api/models/TangRain/SingMOS-Pro and curl -L -s https://huggingface.co/api/models/TangRain/SingingMOS`
- Evidence: Both API requests returned JSON: {"error":"Invalid username or password."}.
- Next diagnostic: Use dataset README's linked GitHub repository https://github.com/South-Twilight/SingMOS/tree/main for pretrained model/code verification instead.

## 2026-06-08 - PMC SVQTD page blocked by browser check

- Context: Trying to open the full PMC page for Paralinguistic singing attribute recognition / SVQTD extraction.
- Command: `web.open https://pmc.ncbi.nlm.nih.gov/articles/PMC9011380/`
- Evidence: Tool returned only 'Checking your browser - reCAPTCHA' with three lines, not article content.
- Next diagnostic: Use SpringerOpen full-text page and YorVoice catalogue entry as alternate sources; optionally retry PMC manually in a browser.

## 2026-06-08 - Seed-VC GitHub tree query glob-expanded by zsh

- Context: Tried to list Seed-VC config/model paths through the GitHub tree API while verifying checkpoint names.
- Command: `curl -L -s https://api.github.com/repos/Plachtaa/seed-vc/git/trees/main?recursive=1 | python3 ...`
- Evidence: zsh: no matches found for the unquoted URL; downstream JSON parser received empty input and raised JSONDecodeError.
- Next diagnostic: Quote URLs containing '?' in zsh, or use the official raw README/inference.py paths; the latter supplied the required checkpoint evidence.

## 2026-06-08 - ScienceDirect MFFMOS page rate limited

- Context: Opening the Applied Acoustics 2026 Reference-free singing voice MOS prediction article through web.open for source extraction.
- Command: `web.open https://www.sciencedirect.com/science/article/pii/S0003682X25004323`
- Evidence: Tool returned: Failed to fetch ... (429) Too Many Requests.
- Next diagnostic: Use previously captured search/curl metadata for high-level survey only; verify full paper/code/data later via DOI or institutional access.

## 2026-06-08 - Arxiv API URL shell glob failure

- Context: Fetching arXiv API metadata for S2Voice, HQ-SVC, NaturalSpeech 3, and Seed-VC
- Command: `curl -sL https://export.arxiv.org/api/query?id_list=2601.13629,2511.08496,2403.03100,2411.09943 | sed -n '1,220p'`
- Evidence: zsh:1: no matches found: https://export.arxiv.org/api/query?id_list=2601.13629,2511.08496,2403.03100,2411.09943
- Next diagnostic: Quote URLs containing '?' before invoking curl under zsh.

## 2026-06-08 - Guessed SVQTD author GitHub repos not found

- Context: Checking whether SVQTD had a public code or data GitHub repository under likely author names.
- Command: `git ls-remote https://github.com/Yanzexu/SVQTD.git and git ls-remote https://github.com/yanzexu/SVQTD.git`
- Evidence: Both returned: remote: Repository not found; fatal: repository not found.
- Next diagnostic: Use https://github.com/hackerpeter1/SVQTD only as the public landing-page source; treat dataset access as request-based and model code unavailable unless authors provide it.

## 2026-06-08 - VocalVerse dataset card README missing

- Context: Checking the Hugging Face dataset card for VocalVerse audio repository metadata.
- Command: `curl -L -s https://huggingface.co/datasets/karl-wang/VocalVerse-dataset/raw/main/README.md`
- Evidence: The endpoint returned: Entry not found.
- Next diagnostic: Use Hugging Face dataset API metadata plus QwenFeat-Vocal-Score README for access and mapping evidence; inspect repository file list if exact counts are needed.

