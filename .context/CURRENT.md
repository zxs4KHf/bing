# Current state

- Last verified: 2026-07-27
- Branch: `codex/claude-recovery-integration`
- Base: public `main` at `bfc3d65` (`Initial public release`)
- Current phase: selectively recover useful interrupted Claude work and prepare it for user validation

## Snapshot

- `[VERIFIED]` The public baseline contains the local Sydney experience tooling, persona preset, research report, and Sydney-ZH training/evaluation pipeline recovered from local commit `7312016`.
- `[VERIFIED]` A fresh public history is being used so private Claude session URLs in the local archival commit messages are not published.
- `[VERIFIED]` `*.exe`, `*.gguf`, `runtime/`, `models/`, `.context/LOCAL.md`, and local history are excluded from Git.
- `[VERIFIED]` Root `README.md` documents project boundaries, quick start, validation status, and third-party licensing; project-owned code and documentation use the MIT License.
- `[VERIFIED]` The original three Claude commits and interrupted WIP snapshot remain preserved on local recovery branches and are not part of this public baseline history.
- `[VERIFIED]` Public repository created at `https://github.com/zxs4KHf/bing`; local `main` tracks `origin/main`.
- `[VERIFIED]` The integration branch adds a corrected API smoke test that reads the actual persona Memory from `sydney_story.json`, sends an explicit Alpaca prompt to `/api/v1/generate`, and validates a non-empty reply. It also adds a BAT entry point and focused persona documentation.

## Verification performed

- Audited tracked files for common credential patterns and machine-specific absolute paths; none found.
- Confirmed the 697,511,936-byte partial GGUF and KoboldCpp executable are ignored and absent from the public tree.
- Previously passed: Python AST checks, JSON/JSONL parsing, persona JSON parsing, and PowerShell parsing for the committed baseline scripts.
- All five current PowerShell scripts pass Windows PowerShell AST parsing; `test_api.ps1` retains a UTF-8 BOM.
- Confirmed the integration branch does not change the baseline launcher or downloader.
- `test_api.ps1` passed a one-shot local mock test: correct endpoint, persona Memory, Alpaca labels, custom question, non-empty response, and exit code 0. Its stopped-service failure path returns exit code 1 with actionable guidance.

## Unknowns and risks

- `[UNKNOWN]` Full model download, GPU inference, API smoke test, persona fidelity, and Chinese quality have not been validated.
- `[DOCUMENTED]` Free Sydney V2 and KoboldCpp are third-party artifacts with their own terms and are not distributed by this repository.
- `[VERIFIED]` The interrupted WIP launcher/download/self-check scripts are known-broken and must not be merged as a unit.

## Next three actions

1. Complete the model download on Wi-Fi and launch KoboldCpp with `Sydney-Experience/launch_sydney.bat`.
2. Run `Sydney-Experience/test_api.bat`, then work through the subjective checklist in `START_HERE.md`.
3. Record persona fidelity and Chinese-quality results; merge this integration branch only after user acceptance.

## Exact resume point

Run `Sydney-Experience/test_api.bat` after the model has finished downloading and `launch_sydney.bat` has loaded it. Record the runtime and subjective results here before merging the integration branch into `main`.
