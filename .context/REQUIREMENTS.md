# Requirements

- Last verified: 2026-07-27
- Sources: user requests on 2026-07-18, 2026-07-26, and 2026-07-27; public project metadata/model cards; local files and observed runtime behavior

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
| REQ-009 | Implemented | [VERIFIED] | Reduce the user's remaining effort to a single double-click: fully unattended resume → verify → launch with no questions asked. | User request on 2026-07-26 ("中间能不问我就不问我"); `一键全自动下载并启动.bat` |
| REQ-010 | Implemented | [VERIFIED] | Design and ship an optimized, reproducible training pipeline for a modern bilingual Sydney: blueprint, hand-authored seed dataset, distillation/cleaning scripts, QLoRA config, fidelity eval suite, and a launcher that can swap in the trained model. | User request on 2026-07-26 ("用你的视角优化训练"); `research/TRAINING_OPTIMIZATION.md`; `training/` |
| REQ-011 | Unknown | [UNKNOWN] | Actually run the training (cloud or local), pass the eval gate against the V2-13B baseline, and adopt the new model. | Requires user to choose route A/B and run the pipeline; blocked on nothing technical |

Allowed statuses: `Implemented`, `Accepted`, `Candidate`, `Deferred`, `Rejected`, `Unknown`.
