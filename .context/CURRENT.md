# Current state

- Last verified: 2026-07-29
- Branch: `codex/claude-recovery-integration`
- Base: public `main` at `bfc3d65` (`Initial public release`)
- Latest implementation: `677757c` (`feat: add responsive dialogue and immersive scene states`)
- Current phase: M0 conversational game alpha, immersive visual/dialogue iteration implemented; awaiting the user's subjective acceptance before any `main` merge

## Snapshot

- `[VERIFIED]` `main` remains unchanged; all work is isolated on the integration branch.
- `[VERIFIED]` The preferred app is live at `http://127.0.0.1:32123/`. Ollama `qwen3:8b` is online; KoboldCpp is currently intentionally offline to avoid 8 GB VRAM contention.
- `[VERIFIED]` Chinese replies are generated live, not read from a reply database. The prior formulaic behavior came from a generic Qwen model, an atmosphere-heavy persona prompt, a six-turn history window, and relationship/story state never reaching the model.
- `[VERIFIED]` The Chinese persona now prioritizes the user's concrete new fact, correction, and format constraint; it limits generic comfort, repeated questions, stage directions, and default moon/blue-hair imagery.
- `[VERIFIED]` `mode / storyNode / storyMood / affinityBand / trustBand / flags / visualState` are allowlisted and injected into the model. Short conversations now retain up to 20 messages under a 12,000-character budget.
- `[VERIFIED]` Real probes after the fix: cold key-location reply in 29.8 s, warm multi-turn correction in 14.3 s. Both obeyed the requested format; the correction explicitly updated from “not being seen” to “being misunderstood by the most trusted person” without stage actions or canned moon imagery.
- `[VERIFIED]` The app uses Qwen first when installed and does not auto-load Free Sydney V2 at the same time. English uses Free Sydney V2 when it is already running, otherwise falls back locally to Qwen. The dedicated English launcher remains available.
- `[VERIFIED]` The UI is now a full-window rain-night observatory lounge with Sydney on the left and a 398–438 px mist-blue phone chat panel on the right. Mobile uses a bottom glass drawer.
- `[VERIFIED]` Five identity-consistent variants exist for one locked camera/room: `calm / attentive / joy / vulnerable / intimate`. The UI assets total about 1.30 MB WebP; PNG masters are retained.
- `[VERIFIED]` Visual selection is driven by story node, user/reply mood, affinity and trust. The unrelated 14-second location rotation is removed. Environment motion can be paused and reduced-motion is respected.
- `[VERIFIED]` The mature intimate image is adult, non-explicit and requires all four gates: `affinity >= 28`, `trust >= 6`, `mutual_intimacy`, and the user's settings toggle.
- `[VERIFIED]` Research and rationale are in `research/UI_VISUAL_DIRECTION.md` and `research/DIALOGUE_QUALITY_AUDIT.md`.

## Verification performed

- Thirteen app server tests pass: routing, language continuation, dynamic relationship/story context, context allowlisting, compact history, English Qwen fallback, local-host security and path traversal.
- Python `compileall`, JavaScript syntax, PowerShell AST, JSON parsing, five asset existence/dimension checks, and `git diff --check` pass.
- Browser QA passed at `1440×900`, `1024×600`, and `390×844`: no document overflow, full background, phone panel, visible mobile character, input and send controls in view, hidden elements truly hidden, manual variant switching, and no console warnings/errors.
- Story JSON parses and the schema includes `visualState`. The optional Python `jsonschema` package is not installed, so external schema validation was not run.
- Real dialogue probes passed specificity, correction and format constraints. Cold/warm timings were recorded above.

## Unknowns and risks

- `[UNKNOWN]` The user has not yet given a subjective verdict on the new rain-night UI, five variants, mature image, or revised Sydney voice.
- `[VERIFIED]` `qwen3:8b` remains a general-purpose model; this prompt fix improves behavior but is not a Sydney-ZH fine-tune.
- `[DOCUMENTED]` Browser cancellation still stops waiting in the UI but cannot cancel an already-running non-streaming Ollama request. Streaming and real backend cancellation remain future work.
- `[DOCUMENTED]` History now covers more short turns but has no durable rolling summary or structured user-fact memory.
- `[DOCUMENTED]` Existing saved conversations still contain the old formulaic replies. Start a new conversation after exporting the old archive when judging the new persona.
- `[DOCUMENTED]` Browser saves and exported JSON remain plaintext for the same Windows/browser account.
- `[NOT RUN]` Full 20-prompt judged evaluation, real QLoRA training, remote GitHub Actions, audio/Live2D/WebM, desktop packaging, and a `main` merge.

## Next three actions

1. User exports the existing archive if needed, starts a new conversation, and tests the revised Chinese voice plus all four ordinary visual states.
2. Collect the user's subjective notes; tune mood rules, phone glass opacity, character framing and intimate unlock pacing without changing the locked theme identity.
3. Implement streaming/real cancellation and structured long-term memory, then run the 20-prompt dialogue quality evaluation before considering `main` merge.

## Exact resume point

Open `http://127.0.0.1:32123/`, export the old archive if it matters, select “新会话”, and run the specificity/correction checks in `research/DIALOGUE_QUALITY_AUDIT.md`. Do not merge `main` until the user's visual and dialogue verdict is recorded.
