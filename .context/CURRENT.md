# Current state

- Last verified: 2026-07-28
- Branch: `codex/claude-recovery-integration`
- Base: public `main` at `bfc3d65` (`Initial public release`)
- Implementation commits: `f9dc676` (runtime/training hardening), `12b72ae` (Moon Window app)
- Current phase: M0 conversational game alpha implemented and running; awaiting the user's subjective acceptance before any `main` merge

## Snapshot

- `[VERIFIED]` `main` remains unchanged; all recovered and new work is isolated on the integration branch.
- `[VERIFIED]` Free Sydney V2 13B Q4_K_M is complete (7,865,956,288 bytes; SHA-256 `a47cb0624d876b6bb0372733e401c7126006390213d5cb99772890b1478604b1`) and KoboldCpp is live on `localhost:5001`.
- `[VERIFIED]` The preferred UI is the independent “Moon Window” PWA at `http://127.0.0.1:32123/`, started by `Sydney-Experience/launch_sydney_app.bat`; KoboldAI Lite is retained only for diagnosis.
- `[VERIFIED]` Chinese messages route locally to Ollama `qwen3:8b`; English remains on Free Sydney V2. Explicit English requests and short-reply language continuity are covered by tests. Failure falls back to KoboldCpp.
- `[VERIFIED]` The app includes normalized local saves/import/export, relationship values, one-time choice effects, story/free-chat layouts, stop-waiting control, privacy notice, and local-data clearing.
- `[VERIFIED]` Four original adult Sydney scenes are in the project: observatory, rainy library, neon rooftop, and ocean dawn. PNG masters are retained; the UI loads ~0.95 MB total WebP variants.
- `[VERIFIED]` Scene transitions include crossfades, slow drift, story-node mapping, manual previous/next, and user-pausable rotation. Reduced-motion and 44 px mobile targets are supported.
- `[VERIFIED]` `prologue.json`, `story.schema.json`, and `scenes.json` establish the Galgame graph/asset boundary. Plans are in `research/GALGAME_PRODUCT_ROADMAP.md` and `research/UI_VISUAL_DIRECTION.md`.
- `[VERIFIED]` The interrupted training/runtime work was reviewed and hardened: deterministic 36/1 data split, malformed-input rejection, local proxy bypass, judge validation/failure codes, Qwen3 QLoRA config, runtime/status/stop helpers, and Windows CI.

## Verification performed

- Nine app server tests pass, including Chinese enhancement, English routing, short Chinese continuity, path traversal, JSON content type, Origin, and DNS-rebinding Host rejection.
- Python `compileall`, JavaScript syntax checks, all JSON/JSONL parsing, five story nodes, four scene assets, all PowerShell AST parsing, and 12 BAT CRLF checks pass.
- Real identity/health reports Moon Window, KoboldCpp, and `qwen3:8b` online. A real Chinese reply returned from the Ollama route with `language=zh` and no fallback.
- Browser QA passed at 1024×600 and 390×844: no horizontal overflow, 58% story stage / 44% chat stage, 44 px mobile controls, mode switching, settings, choices, formatted actions, and manual scene rotation.
- `git diff --check` and a common credential-pattern scan passed before commits.

## Unknowns and risks

- `[UNKNOWN]` The user has not yet given a final subjective verdict on the newest four-scene UI, character art, and Sydney fidelity.
- `[VERIFIED]` Free Sydney V2 still has weak Chinese; acceptable Chinese currently depends on general-purpose `qwen3:8b`, not a completed Sydney-ZH fine-tune.
- `[DOCUMENTED]` Browser saves and exported JSON are plaintext for the same Windows/browser account. No cloud sync or encryption is implemented.
- `[DOCUMENTED]` PWA packaging is implemented; Tauri, formal save slots/rollback, full chapters, audio, Live2D/WebM, and a complete Galgame asset set are later milestones.
- `[VERIFIED]` Three new image variants succeeded; a fourth winter-conservatory generation hit the image service usage limit and is not referenced.
- `[NOT RUN]` Full 20-prompt judged evaluation, real QLoRA training, external distillation APIs, live large downloads, remote GitHub Actions, and a `main` merge.

## Next three actions

1. User tests the open Moon Window page: Chinese conversation, four scene controls, story/free-chat switch, save export, and character/visual taste.
2. Address subjective feedback; then expand the vertical slice with deterministic node text, `affinity/trust/boundaries`, checkpoints, and the next image batch when capacity returns.
3. If accepted, merge the integration branch into `main`; otherwise keep `main` unchanged and iterate here.

## Exact resume point

Run `Sydney-Experience\launch_sydney_app.bat`, open `http://127.0.0.1:32123/`, and begin with the user's visual/character acceptance checklist. Do not merge `main` until that verdict is recorded.
