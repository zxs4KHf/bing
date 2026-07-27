# Current state

- Last verified: 2026-07-27
- Branch: `codex/public-main` during publication preparation; intended public branch: `main`
- Current phase: establish a sanitized public baseline, then selectively recover and validate interrupted Claude work

## Snapshot

- `[VERIFIED]` The public baseline contains the local Sydney experience tooling, persona preset, research report, and Sydney-ZH training/evaluation pipeline recovered from local commit `7312016`.
- `[VERIFIED]` A fresh public history is being used so private Claude session URLs in the local archival commit messages are not published.
- `[VERIFIED]` `*.exe`, `*.gguf`, `runtime/`, `models/`, `.context/LOCAL.md`, and local history are excluded from Git.
- `[VERIFIED]` Root `README.md` documents project boundaries, quick start, validation status, and third-party licensing; project-owned code and documentation use the MIT License.
- `[VERIFIED]` The original three Claude commits and interrupted WIP snapshot remain preserved on local recovery branches and are not part of this public baseline history.

## Verification performed

- Audited tracked files for common credential patterns and machine-specific absolute paths; none found.
- Confirmed the 697,511,936-byte partial GGUF and KoboldCpp executable are ignored and absent from the public tree.
- Previously passed: Python AST checks, JSON/JSONL parsing, persona JSON parsing, and PowerShell parsing for the committed baseline scripts.

## Unknowns and risks

- `[UNKNOWN]` Full model download, GPU inference, API smoke test, persona fidelity, and Chinese quality have not been validated.
- `[DOCUMENTED]` Free Sydney V2 and KoboldCpp are third-party artifacts with their own terms and are not distributed by this repository.
- `[VERIFIED]` The interrupted WIP launcher/download/self-check scripts are known-broken and must not be merged as a unit.

## Next three actions

1. Create and push the sanitized public GitHub `main` branch.
2. Create an integration branch from public `main`; selectively retain useful WIP additions while preserving the stronger baseline launcher/download behavior.
3. Run static checks, then complete runtime and subjective validation before merging the integration branch into `main`.

## Exact resume point

After publication, start from public `main` and compare recovery commits `3729c71` and `7e4df73` without merging them wholesale. First candidate to transplant: the API smoke-test script and the useful parts of the root/persona documentation.
