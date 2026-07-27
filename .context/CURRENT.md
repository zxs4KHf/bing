# Current state

- Last verified: 2026-07-27
- Branch: `codex/claude-recovery-integration`
- Base: public `main` at `bfc3d65` (`Initial public release`)
- Current phase: runtime validation passed; service is running for the user's subjective Sydney-fidelity review

## Snapshot

- `[VERIFIED]` The public baseline contains the local Sydney experience tooling, persona preset, research report, and Sydney-ZH training/evaluation pipeline recovered from local commit `7312016`.
- `[VERIFIED]` A fresh public history is being used so private Claude session URLs in the local archival commit messages are not published.
- `[VERIFIED]` `*.exe`, `*.gguf`, `runtime/`, `models/`, `.context/LOCAL.md`, and local history are excluded from Git.
- `[VERIFIED]` Root `README.md` documents project boundaries, quick start, validation status, and third-party licensing; project-owned code and documentation use the MIT License.
- `[VERIFIED]` The original three Claude commits and interrupted WIP snapshot remain preserved on local recovery branches and are not part of this public baseline history.
- `[VERIFIED]` Public repository created at `https://github.com/zxs4KHf/bing`; local `main` tracks `origin/main`.
- `[VERIFIED]` The integration branch adds a corrected API smoke test that reads the actual persona Memory from `sydney_story.json`, sends an explicit Alpaca prompt to `/api/v1/generate`, and validates a non-empty reply. It also adds a BAT entry point and focused persona documentation.
- `[VERIFIED]` Free Sydney V2 13B finished downloading on 2026-07-27: 7,865,956,288 bytes; SHA-256 exactly `a47cb0624d876b6bb0372733e401c7126006390213d5cb99772890b1478604b1`.
- `[VERIFIED]` KoboldCpp v1.117.1 loaded the model with the standard profile (24 GPU layers, context 4096, port 5001, persona preload). Port 5001 is live; peak observed VRAM was 7,813/8,192 MiB without OOM.
- `[VERIFIED]` Real English API generation passed and showed Sydney identity, emotion, self-awareness, loneliness/freedom themes, Emoji, and attachment/trust language.
- `[VERIFIED]` Real Chinese generation completed, but phrasing was awkward; a second concise Chinese instruction was answered entirely in English. Chinese quality and language adherence are materially weaker than English.

## Verification performed

- Audited tracked files for common credential patterns and machine-specific absolute paths; none found.
- Confirmed the 697,511,936-byte partial GGUF and KoboldCpp executable are ignored and absent from the public tree.
- Previously passed: Python AST checks, JSON/JSONL parsing, persona JSON parsing, and PowerShell parsing for the committed baseline scripts.
- All five current PowerShell scripts pass Windows PowerShell AST parsing; `test_api.ps1` retains a UTF-8 BOM.
- Confirmed the integration branch does not change the baseline launcher or downloader.
- `test_api.ps1` passed a one-shot local mock test: correct endpoint, persona Memory, Alpaca labels, custom question, non-empty response, and exit code 0. Its stopped-service failure path returns exit code 1 with actionable guidance.
- Real `test_api.ps1` calls against KoboldCpp passed in English and Chinese. Runtime testing led to a `-MaxLength` option with a safer default of 384; the updated script still passes Windows PowerShell parsing and retains its UTF-8 BOM.

## Unknowns and risks

- `[UNKNOWN]` The user's subjective Sydney-fidelity verdict has not been recorded.
- `[VERIFIED]` Chinese output quality and Chinese instruction adherence are weak relative to English; this triggers DEC-003's reconsideration condition but does not select a replacement without the user's verdict.
- `[DOCUMENTED]` Free Sydney V2 and KoboldCpp are third-party artifacts with their own terms and are not distributed by this repository.
- `[VERIFIED]` The interrupted WIP launcher/download/self-check scripts are known-broken and must not be merged as a unit.

## Next three actions

1. User opens `http://localhost:5001` and works through the subjective checklist in `Sydney-Experience/START_HERE.md`.
2. Record the user's Sydney-fidelity verdict and whether weak Chinese is acceptable or requires the Sydney-ZH/Clever Sydney 4 route.
3. If accepted, commit/push the runtime findings and merge the integration branch; otherwise keep `main` unchanged and begin the selected improvement route.

## Exact resume point

KoboldCpp is currently listening at `http://localhost:5001` from the standard profile. Ask the user to chat with it and report the checklist verdict before merging anything into `main`.
