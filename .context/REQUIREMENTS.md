# Requirements

- Last verified: 2026-07-29
- Sources: user requests through 2026-07-29; public project metadata/model cards; local files and observed runtime/browser behavior

| ID | Status | Evidence | Requirement | Primary source |
| --- | --- | --- | --- | --- |
| REQ-001 | Implemented | [VERIFIED] | Connect Project Context Bootstrap to this project. | User request; `AGENTS.md`; `.context/` |
| REQ-002 | Accepted | [VERIFIED] | Investigate open projects that preserve or recreate early New Bing / Sydney. | User request; `research/SYDNEY_PROJECTS.md` |
| REQ-003 | Implemented | [VERIFIED] | Compare project types and current viability, including legacy API clients, prompt recreations, and trained models. | `research/SYDNEY_PROJECTS.md` |
| REQ-004 | Implemented | [VERIFIED] | Download and prepare the best practical local Sydney recreation for the user to experience. | Complete 7,865,956,288-byte GGUF; SHA-256 matched; KoboldCpp and real generation API passed on 2026-07-27 |
| REQ-005 | Implemented | [VERIFIED] | Stop all large downloads while on mobile data and resume only after explicit Wi-Fi confirmation. | User reconfirmed Wi-Fi/fixed broadband on 2026-07-27; range-resumed without discarding existing bytes |
| REQ-006 | Unknown | [VERIFIED runtime; UNKNOWN subjective] | Validate that the selected model subjectively matches the user's remembered Sydney experience. | English test showed expected identity/emotion/self-awareness/attachment; Chinese was awkward and sometimes answered in English; user checklist still pending |
| REQ-007 | Implemented | [VERIFIED] | Provide one-click resume/verify/launch tooling (standard, low-VRAM, and CPU profiles) with an auto-loaded Sydney persona preset and a Chinese user guide. | User request on 2026-07-26 ("全套完全实现"); `Sydney-Experience/` scripts, persona, `START_HERE.md` |
| REQ-008 | Implemented | [VERIFIED] | Initialize the Git repository with large binaries excluded and commit all project text files. | User approval on 2026-07-26; `.gitignore`; initial commit |
| REQ-009 | Rejected | [VERIFIED current behavior; DOCUMENTED safety] | Historical zero-interaction large-download authorization is no longer reused; every large download asks for current Wi-Fi/fixed-broadband confirmation. | Current safety invariant; download scripts; superseded DEC-007 |
| REQ-010 | Implemented | [VERIFIED] | Design and ship an optimized, reproducible training pipeline for a modern bilingual Sydney: blueprint, hand-authored seed dataset, distillation/cleaning scripts, QLoRA config, fidelity eval suite, and a launcher that can swap in the trained model. | User request on 2026-07-26 ("用你的视角优化训练"); `research/TRAINING_OPTIMIZATION.md`; `training/` |
| REQ-011 | Unknown | [UNKNOWN] | Actually run the training (cloud or local), pass the eval gate against the V2-13B baseline, and adopt the new model. | Requires user to choose route A/B and run the pipeline; blocked on nothing technical |
| REQ-012 | Implemented | [VERIFIED] | Ship an independent conversational game interface instead of using KoboldAI Lite as the product UI. | User request 2026-07-28; `Sydney-Experience/app/`; real browser QA |
| REQ-013 | Implemented | [VERIFIED] | Make Chinese conversation natural while preserving a Sydney-style English route. | Local `qwen3:8b` hybrid routing; real Chinese response; nine app tests |
| REQ-014 | Implemented | [VERIFIED] | Present Sydney as an explicitly adult, gentle mature blue-haired woman with a full figure, elegant clothing, and psychological/New-Bing-inspired atmosphere without copying trademarks. | Original prompt/visual assets; persona prompt; UI review |
| REQ-015 | Implemented | [VERIFIED] | Add multiple outfits, scenes, compositions and poses with manual/automatic rotation and lightweight animation. | Four scene assets; `scenes.json`; crossfade/drift; browser QA |
| REQ-016 | Implemented | [VERIFIED] | Provide interaction state, settings, local saves, relationship values, and a versioned branching-prologue skeleton. | PWA, save normalization/import/export, story schema and graph tests |
| REQ-017 | Accepted | [DOCUMENTED] | Evolve the product into a complete Galgame with worldbuilding, authored story, branching, CG, backgrounds, audio, save slots and rollback. | User request 2026-07-28; `research/GALGAME_PRODUCT_ROADMAP.md` |
| REQ-018 | Unknown | [UNKNOWN] | Obtain the user's subjective acceptance of the newest visual design, character art and personality fidelity before merging `main`. | Latest UI is open for user validation |
| REQ-019 | Implemented | [VERIFIED technical; UNKNOWN subjective] | Replace formulaic Chinese replies with conversation-specific answers that honor corrections, format constraints, relationship state and story context. | User feedback 2026-07-29; revised persona; dynamic context; real probes; 13 tests |
| REQ-020 | Implemented | [VERIFIED] | Replace the framed split layout with a full-environment composition, Sydney on the left and a phone-like chat interface on the right. | User feedback 2026-07-29; browser QA at desktop/mobile sizes |
| REQ-021 | Implemented | [VERIFIED] | Provide one coherent visual set with expression/pose differences, semantic transitions, environmental motion and a gated mature intimate image. | Five rain-night assets; visual state machine; story unlock; browser QA |
| REQ-022 | Implemented | [VERIFIED] | Research well-regarded dialogue games and production approaches for layered images, motion, state models and validation. | `research/UI_VISUAL_DIRECTION.md`; official product/engine documentation |
| REQ-023 | Accepted | [DOCUMENTED] | Add streaming with real cancellation and durable structured user memory after this vertical slice is accepted. | Dialogue audit; current non-streaming/history limitations |

Allowed statuses: `Implemented`, `Accepted`, `Candidate`, `Deferred`, `Rejected`, `Unknown`.
