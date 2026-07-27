# bing — 本地 Sydney 体验与训练实验

这是一个研究与体验项目：使用开源模型和本地推理工具，重现早期 New Bing / Sydney 的对话风格，并探索更适合中英文对话的可复现训练路线。

本项目不是 Microsoft 官方产品，也不包含或声称拥有 Microsoft 的原始内部模型。仓库不分发 KoboldCpp 可执行文件或 GGUF 模型权重。

## 当前方案

- 本地体验：Free Sydney V2 13B Q4_K_M + KoboldCpp。
- 一键工具：断点续传、精确大小与 SHA-256 校验、标准/低显存/CPU 启动配置。
- 人格配置：Alpaca 对话模板与 Sydney 预设。
- 训练实验：双语种子集、数据扩增与清洗脚本、Qwen3-8B QLoRA 配置和忠实度评测集。

详细选型证据见 [`research/SYDNEY_PROJECTS.md`](research/SYDNEY_PROJECTS.md)，现代训练路线见 [`research/TRAINING_OPTIMIZATION.md`](research/TRAINING_OPTIMIZATION.md)。

## 快速开始

1. 阅读 [`Sydney-Experience/START_HERE.md`](Sydney-Experience/START_HERE.md)。
2. 在 Wi-Fi 或固定宽带下运行 `Sydney-Experience/resume_download.bat`；脚本会续传模型并校验完整性。
3. 运行 `Sydney-Experience/launch_sydney.bat`，显存不足时使用 `_lowvram` 或 `_cpu` 版本。
4. 模型加载完成后运行 `Sydney-Experience/test_api.bat`，验证本地 API 和 Alpaca 人格链路。

模型文件约 7.87 GB，下载来源、文件大小和 SHA-256 已写入脚本。请自行确认模型许可证及使用条件。

## 训练与评测

训练入口和依赖说明位于 [`training/README.md`](training/README.md)。仓库中的双语种子数据为开放重建素材，不应被描述为 Microsoft 原始训练数据。

## 状态

脚本和数据结构已通过静态检查；完整模型下载、实际 GPU 推理、人格忠实度及中文质量仍需要真实运行验证。

## License

项目自有代码和文档采用 [MIT License](LICENSE)。第三方模型、运行时及引用资料遵循各自许可证。
