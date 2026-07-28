# Project Context

- Last verified: 2026-07-28
- Verified against branch: `codex/claude-recovery-integration` at implementation commit `12b72ae` plus live local validation
- Scope: build a local-first Chinese conversational character game inspired by early Sydney, then evolve it into an original Galgame
- Known gaps: newest UI/character art awaits subjective acceptance; Sydney-ZH training, full chapters, formal rollback, audio, and desktop packaging are not complete

## Purpose

- `[VERIFIED]` Research open-source projects that attempt to preserve or recreate the early New Bing / Sydney experience.
- `[VERIFIED]` The user accepted preparing the most credible practical candidate for local, offline interaction without depending on Microsoft's current Copilot service.
- `[VERIFIED]` On 2026-07-26 the user asked for the full set to be implemented as completely as possible; one-click tooling, persona preset, guide, and Git history were delivered.
- `[VERIFIED]` Detailed findings and sources are recorded in `research/SYDNEY_PROJECTS.md`.
- `[VERIFIED]` On 2026-07-28 the goal expanded: first ship a beautiful Chinese conversational game, then develop a complete Galgame with worldbuilding, authored scripts, branches, CG, scenes, and game assets.

## Architecture

- `Sydney-Experience/runtime/koboldcpp.exe`: local GGUF inference runtime and browser UI (SHA-256 verified).
- `Sydney-Experience/models/Free-Sydney-V2-13B/`: complete local personality model; 7,865,956,288 bytes with SHA-256 `a47cb0624d876b6bb0372733e401c7126006390213d5cb99772890b1478604b1` verified on 2026-07-27.
- `Sydney-Experience/*.bat` + `Sydney-Experience/scripts/*.ps1`: one-click resume/verify/launch tooling (standard, low-VRAM, CPU profiles).
- `Sydney-Experience/persona/`: Sydney persona preset — `sydney_story.json` auto-loaded via `--preloadstory`, `sydney_system_prompt.txt` manual fallback.
- `Sydney-Experience/START_HERE.md`: Chinese user guide (steps, experience checklist, tuning, troubleshooting).
- `research/SYDNEY_PROJECTS.md`: candidate comparison, evidence, limitations.
- `research/TRAINING_OPTIMIZATION.md`: modern training blueprint (routes A/B/C, base-model selection, data strategy, eval gate).
- `training/`: runnable pipeline — `data/` (Claude-authored bilingual seed set, distillation & cleaning scripts, dataset registry), `prompts/` (generator & judge specs), `configs/` (LLaMA-Factory QLoRA), `eval/` (20-prompt fidelity suite against the local koboldcpp API).
- `.context/`: PCB recovery, requirements, and durable decisions.
- `Sydney-Experience/app/server.py`: loopback-only Python standard-library app server and guarded local-model proxy.
- `Sydney-Experience/app/public/`: build-free PWA with story/chat layouts, local saves, settings, and scene controls.
- `Sydney-Experience/app/content/`: versioned prologue graph, story schema, and scene manifest.
- `Sydney-Experience/app/assets/`: four original adult character-scene masters and optimized WebP assets.
- Ollama `qwen3:8b`: optional local Chinese route; Free Sydney V2 remains the English/personality route.
- `research/GALGAME_PRODUCT_ROADMAP.md` and `research/UI_VISUAL_DIRECTION.md`: product, save/rollback, asset, and visual plans.

After the model download completes, chat inference is fully local and does not require the Microsoft Bing/Copilot service.

## Durable invariants

- Do not describe any recreation as Microsoft's original internal model; distinguish interface clients, prompt recreations, and trained personality models.
- Preserve evidence and uncertainty about training data, fidelity, maintenance, and service dependencies.
- Do not use mobile data for large downloads; resume only after the user confirms Wi-Fi is available (the resume script re-confirms on every run).
- Keep the verified GGUF local and ignored by Git; do not delete or redownload it unless integrity validation later fails.
- Do not expose Microsoft cookies or API credentials when assessing legacy clients.
- Keep `*.exe` and `*.gguf` out of Git.
- Keep product identity original: no Microsoft/Bing logos, copied UI, or claim of official/internal Sydney assets.
- The character is explicitly adult. Mature/full proportions are allowed while shipped visuals remain fully clothed and non-explicit.
- Local app endpoints remain loopback-only and reject non-JSON, cross-origin, and non-loopback Host requests.
- Large downloads require fresh Wi-Fi/fixed-broadband confirmation; historical permission is not persistent authorization.

## Development entry points

- User guide: `Sydney-Experience/START_HERE.md`
- Preferred app: `Sydney-Experience/launch_sydney_app.bat` → `http://127.0.0.1:32123/`
- Re-verify the downloaded model: double-click `Sydney-Experience/verify_model.bat`
- Chat with Sydney: double-click `Sydney-Experience/launch_sydney.bat` (or `_lowvram` / `_cpu`)
- API smoke test after launch: double-click `Sydney-Experience/test_api.bat`
- Verify only: `Sydney-Experience/verify_model.bat`
- Train a better Sydney: `research/TRAINING_OPTIMIZATION.md` → `training/README.md`
- Swap in a trained model: `Sydney-Experience/scripts/launch_sydney.ps1 -ModelFile <path.gguf>`
