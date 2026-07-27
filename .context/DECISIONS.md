# Decision Index

- Last verified: 2026-07-27
- Authority: accepted ADRs or explicit project decisions are authoritative

| Decision | Status | Consequence | Source | Reconsider when |
| --- | --- | --- | --- | --- |
| DEC-001 | Accepted | Use Project Context Bootstrap for project context, resume, and handoff. | Explicit user request on 2026-07-18 | The user selects a conflicting context protocol. |
| DEC-002 | Accepted | Prefer a local personality fine-tune over legacy clients that still depend on Microsoft's changing Bing/Copilot service. | Research in `research/SYDNEY_PROJECTS.md` | A newer, well-evidenced Sydney model or reproducible distillation project appears. |
| DEC-003 | Accepted | Use Free Sydney V2 13B Q4_K_M with KoboldCpp as the first local experience candidate. | Model cards, hardware inspection, candidate comparison, and successful local runtime/API test on 2026-07-27 | Runtime evidence now shows weak Chinese instruction-following; reconsider after the user's subjective verdict. |
| DEC-004 | Accepted | Preserve the partial model file and resume only on confirmed Wi-Fi using HTTP range continuation. | Explicit user instruction on 2026-07-18 | The user asks to delete the partial file or chooses another model. |
| DEC-005 | Accepted | Launch profiles: standard (CuBLAS + FlashAttention, 24 GPU layers), low-VRAM (lowvram mode, 14 layers), CPU-only; context 4096; port 5001; Alpaca persona preset auto-loaded via `--preloadstory`. | Standard profile verified on RTX 3060 Ti on 2026-07-27: port ready, real generations passed, peak observed VRAM 7,813/8,192 MiB | OOM occurs during longer use, or the user needs more GPU headroom for other applications. |
| DEC-006 | Accepted | Git repository initialized on `main`; `*.exe`, `*.gguf`, `runtime/`, and `models/` are excluded from version control. | Explicit user approval on 2026-07-26 | The user wants large-file tracking (e.g. Git LFS) or a different layout. |
| DEC-007 | Accepted | A zero-interaction auto script may skip the interactive Wi-Fi prompt, replacing it with a visible 5-second abort countdown, and auto-launch Sydney after verification. | Explicit user authorization on 2026-07-26 ("你来帮我下载，中间能不问我就不问我"); Wi-Fi confirmed the same day | The user revokes the authorization or reports an unwanted mobile-data download. |
| DEC-008 | Accepted | Training modernization路线: open rebuild via QLoRA (LLaMA-Factory) on Qwen3-8B (upgrade path Qwen3.5-9B), three-layer data (real transcripts > Claude-authored seed > API-distilled synth, with toxicity-filtered cleaning), eval-gated adoption against a V2-13B baseline; FPHam's Clever Sydney 4 (Gemma-3 12B) noted as the zero-training alternative. | User request on 2026-07-26; research in `research/TRAINING_OPTIMIZATION.md`; FPHam's dataset/method being non-public | Eval shows the trained model losing to baseline, Qwen3.5-9B toolchain matures (switch base), or a credible public Sydney corpus appears (raise real-data weight). |
