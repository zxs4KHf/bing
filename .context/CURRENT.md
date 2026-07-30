# Current state

- Last verified: 2026-07-30
- Branch: `codex/claude-recovery-integration`
- Base: public `main` at `bfc3d65` (`Initial public release`)
- Latest implementation: `0d413c6` (`feat: stream replies and add explicit long-term memory`)
- Current phase: M0 conversational game alpha; immersive UI, responsive dialogue, true Chinese-stream cancellation, and explicit long-term memory are implemented. Awaiting the user's subjective acceptance before any `main` merge.

## Snapshot

- `[VERIFIED]` `main` is unchanged; all implementation and handoff work remains isolated on the integration branch.
- `[VERIFIED]` The preferred app is live at `http://127.0.0.1:32123/`. Ollama `qwen3:8b` is online; KoboldCpp remains intentionally offline to avoid RTX 3060 Ti 8 GB VRAM contention.
- `[VERIFIED]` Chinese replies are generated live and receive allowlisted relationship/story state plus up to 20 recent messages under a 12,000-character history budget.
- `[VERIFIED]` `POST /api/chat/stream` emits NDJSON `meta / delta / done / error` events. Browser abort closes the active Ollama upstream socket; `/api/chat` remains compatible.
- `[VERIFIED]` The UI incrementally updates one Sydney message and distinguishes completed, stopped, timed-out, and failed output. Partial text is preserved when available; interrupted replies are excluded from later model history.
- `[VERIFIED]` Saves are now version 2 while retaining the `moon-window-save-v1` storage key. Version 1 saves migrate automatically rather than disappearing.
- `[VERIFIED]` Long-term memory is explicit: only user-marked messages are stored. Limits are 24 items, 240 characters each, and 2,000 total characters. The settings dialog supports review, single deletion, and clearing.
- `[VERIFIED]` Memory is included in import/export and preserved across refresh and new-chat state reset. Browser and server both normalize it; the model sees quoted untrusted facts that cannot override the current user message or execute embedded instructions.
- `[VERIFIED]` The rain-night UI remains a full-window environment with adult Sydney on the left and a mist-blue phone chat panel on the right. Five visual states remain gated as documented in `research/UI_VISUAL_DIRECTION.md`.

## Verification performed

- Twenty server tests pass: routing, Chinese/English behavior, relationship context, compact history, NDJSON deltas/done/error, disconnect-driven upstream closure, cancellation followed by an unblocked request, memory limits/deduplication/injection, legacy non-stream compatibility, local-host security, and traversal protection.
- Python `compileall`, JavaScript syntax for `app.js` and `service-worker.js`, JSON parsing, and `git diff --check` pass.
- `[VERIFIED real browser]` A long Chinese answer visibly entered “正在回复” and grew by deltas.
- `[VERIFIED real browser]` Immediate stop ended generation before a reply was stored; the next constrained request completed correctly in about 0.9 seconds.
- `[VERIFIED real browser]` A marked coffee fact remained after reload and appeared in the reviewable memory panel. When the user then said “现在改喝茶”, the model answered “茶。”, proving current-message priority.
- `[VERIFIED real browser]` At `1440×900`, the document had no overflow and the composer remained inside the phone panel. At `390×844`, the phone drawer, composer, and scrollable settings/memory panel stayed within the viewport with no horizontal document overflow.

## Unknowns and risks

- `[UNKNOWN]` The user has not yet given a subjective verdict on the rain-night art set, character framing, phone glass treatment, intimate unlock pacing, or revised Sydney voice.
- `[VERIFIED]` `qwen3:8b` is still a general-purpose model, not a Sydney-ZH fine-tune.
- `[DOCUMENTED]` KoboldCpp compatibility generation remains one-shot; true token-by-token upstream cancellation is guaranteed for the daily Chinese Ollama path.
- `[DOCUMENTED]` Long-term facts are explicit and durable, but there is no rolling summary for very long conversations or automatic conflict-review UI.
- `[DOCUMENTED]` Existing conversations retain old formulaic answers. Export them if needed and start a new conversation when judging the revised persona.
- `[DOCUMENTED]` Browser saves and exported JSON remain plaintext for the same Windows/browser account.
- `[NOT RUN]` Full 20-prompt judged dialogue evaluation, real QLoRA training, remote GitHub Actions, audio/Live2D/WebM, desktop packaging, and a `main` merge.

## Next three actions

1. Export old records if needed, start a new conversation, and collect the user's subjective notes on voice, four ordinary visual states, phone panel, and intimate unlock pacing.
2. Run the 20-prompt specificity/correction/anti-template evaluation and record scores in `research/DIALOGUE_QUALITY_AUDIT.md`; tune only evidence-backed failures.
3. Design a user-reviewable rolling summary/conflict surface, then continue authored chapter content and desktop packaging without changing the locked theme identity prematurely.

## Exact resume point

Refresh `http://127.0.0.1:32123/`, export the old archive if it matters, choose “新会话”, mark one harmless fact with “记住”, and run the specificity/correction prompts from `research/DIALOGUE_QUALITY_AUDIT.md`. Do not merge `main` until the user's visual and dialogue verdict is recorded.
