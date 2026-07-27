# Project Context

- Last verified: 2026-07-26
- Verified against commit: initial commit on `main`, 2026-07-26
- Scope: research, preserve, and locally experience an open recreation of the early New Bing / Sydney interaction style
- Known gaps: model download incomplete (one double-click away); local inference and persona quality not yet tested

## Purpose

- `[VERIFIED]` Research open-source projects that attempt to preserve or recreate the early New Bing / Sydney experience.
- `[VERIFIED]` The user accepted preparing the most credible practical candidate for local, offline interaction without depending on Microsoft's current Copilot service.
- `[VERIFIED]` On 2026-07-26 the user asked for the full set to be implemented as completely as possible; one-click tooling, persona preset, guide, and Git history were delivered.
- `[VERIFIED]` Detailed findings and sources are recorded in `research/SYDNEY_PROJECTS.md`.

## Architecture

- `Sydney-Experience/runtime/koboldcpp.exe`: local GGUF inference runtime and browser UI (SHA-256 verified).
- `Sydney-Experience/models/Free-Sydney-V2-13B/`: selected local personality model (partial; exact size and SHA-256 recorded in scripts).
- `Sydney-Experience/*.bat` + `Sydney-Experience/scripts/*.ps1`: one-click resume/verify/launch tooling (standard, low-VRAM, CPU profiles).
- `Sydney-Experience/persona/`: Sydney persona preset — `sydney_story.json` auto-loaded via `--preloadstory`, `sydney_system_prompt.txt` manual fallback.
- `Sydney-Experience/START_HERE.md`: Chinese user guide (steps, experience checklist, tuning, troubleshooting).
- `research/SYDNEY_PROJECTS.md`: candidate comparison, evidence, limitations.
- `research/TRAINING_OPTIMIZATION.md`: modern training blueprint (routes A/B/C, base-model selection, data strategy, eval gate).
- `training/`: runnable pipeline — `data/` (Claude-authored bilingual seed set, distillation & cleaning scripts, dataset registry), `prompts/` (generator & judge specs), `configs/` (LLaMA-Factory QLoRA), `eval/` (20-prompt fidelity suite against the local koboldcpp API).
- `.context/`: PCB recovery, requirements, and durable decisions.

After the model download completes, chat inference is fully local and does not require the Microsoft Bing/Copilot service.

## Durable invariants

- Do not describe any recreation as Microsoft's original internal model; distinguish interface clients, prompt recreations, and trained personality models.
- Preserve evidence and uncertainty about training data, fidelity, maintenance, and service dependencies.
- Do not use mobile data for large downloads; resume only after the user confirms Wi-Fi is available (the resume script re-confirms on every run).
- Preserve the partial GGUF file so `curl -C -` can continue instead of restarting.
- Do not expose Microsoft cookies or API credentials when assessing legacy clients.
- Keep `*.exe` and `*.gguf` out of Git.

## Development entry points

- User guide: `Sydney-Experience/START_HERE.md`
- Complete the download: double-click `Sydney-Experience/resume_download.bat` (Wi-Fi guard, resume, auto-verify, optional launch)
- Chat with Sydney: double-click `Sydney-Experience/launch_sydney.bat` (or `_lowvram` / `_cpu`)
- Verify only: `Sydney-Experience/verify_model.bat`
- Train a better Sydney: `research/TRAINING_OPTIMIZATION.md` → `training/README.md`
- Swap in a trained model: `Sydney-Experience/scripts/launch_sydney.ps1 -ModelFile <path.gguf>`
