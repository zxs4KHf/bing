# 月窗：本地 Sydney 风格对话应用与训练实验

“月窗”是一个本地优先的中文角色对话游戏，也是一套研究早期 New Bing / Sydney 交互风格的开放实验。当前版本提供独立聊天界面、原创成年角色视觉、本地关系状态、序章分支骨架和可选中文增强；后续计划演进为带完整章节、分支、CG、场景与存档回滚的 Galgame。

本项目不是 Microsoft 官方产品，不包含或声称拥有 Microsoft 的原始内部模型，也不使用 Bing/Microsoft 商标作为产品身份。仓库不分发 KoboldCpp 可执行文件或 GGUF 模型权重。

## 首选启动方式

在已经准备好运行时和模型的电脑上，双击：

```text
Sydney-Experience\launch_sydney_app.bat
```

启动器会复用或后台启动 KoboldCpp，然后打开 `http://127.0.0.1:32123/` 的“月窗”界面。支持的浏览器可将它安装为独立 PWA 窗口。

完整说明见 [`Sydney-Experience/START_HERE.md`](Sydney-Experience/START_HERE.md)。旧的 `launch_sydney.bat` 仍保留，主要用于 KoboldCpp 原生界面诊断；日常聊天优先使用“月窗”。

## 首次准备新电脑

需要 Windows、Python 3.10 或更高版本，以及 Wi-Fi/固定宽带。大文件下载前脚本会再次确认网络。

1. 双击 `Sydney-Experience/setup_runtime.bat`，下载并校验 KoboldCpp（约 637 MB）。
2. 双击 `Sydney-Experience/resume_download.bat`，下载并校验 Free Sydney V2 13B Q4_K_M（约 7.87 GB，支持断点续传）。
3. 双击 `Sydney-Experience/launch_sydney_app.bat` 开始聊天。

### 可选：增强中文

Free Sydney V2 使用较早的 Llama 2 底座，中文能力弱于英文。安装 [Ollama](https://ollama.com/download/windows) 后，双击：

```text
Sydney-Experience\setup_chinese_model.bat
```

脚本会在明确确认 Wi-Fi/固定宽带后安装 `qwen3:8b`（约 5.2 GB）。月窗检测到它时，会把中文对话交给本地 Qwen3 做自然中文增强，英文仍使用 Free Sydney V2；Ollama 不可用时会自动回退。这个双模型路由是阶段性方案，长期目标仍是通过评测的 Sydney-ZH 单模型。

## 当前能力与状态

- `[VERIFIED]` Free Sydney V2 13B 模型已在开发机完整下载并通过大小、SHA-256、真实 GPU 推理和 API 测试。
- `[VERIFIED]` `qwen3:8b` 已在开发机安装；月窗具备中文优先路由和回退机制。
- `[VERIFIED]` 已有独立 HTML/CSS/JavaScript PWA、Python 本地代理、4 幅原创角色场景、双模式布局、关系值、剧情变量、序章选择和本地 JSON 存档。
- `[VERIFIED]` 真实中文混合路由、1024×600 桌面与 390×844 移动布局、场景轮切及关键交互均已通过浏览器走查。
- `[DOCUMENTED]` 长期中文质量评测、完整章节内容、正式存档槽/回滚和桌面安装包仍是下一阶段工作。

项目入口：

- 对话应用说明：[`Sydney-Experience/app/README.md`](Sydney-Experience/app/README.md)
- Galgame 产品与架构路线：[`research/GALGAME_PRODUCT_ROADMAP.md`](research/GALGAME_PRODUCT_ROADMAP.md)
- 视觉与交互方向：[`research/UI_VISUAL_DIRECTION.md`](research/UI_VISUAL_DIRECTION.md)
- Sydney 项目调研：[`research/SYDNEY_PROJECTS.md`](research/SYDNEY_PROJECTS.md)
- 中文训练路线：[`research/TRAINING_OPTIMIZATION.md`](research/TRAINING_OPTIMIZATION.md)
- 训练与评测操作：[`training/README.md`](training/README.md)

## 主要目录

```text
Sydney-Experience/
├── launch_sydney_app.bat       # 首选：启动月窗应用
├── setup_runtime.bat           # 准备 KoboldCpp
├── resume_download.bat         # 准备 Free Sydney V2 模型
├── setup_chinese_model.bat     # 可选：准备 qwen3:8b 中文增强
├── app/                        # 本地服务器、PWA、剧情与原创素材
├── persona/                    # Sydney 风格人格配置
├── scripts/                    # Windows 启动和运维脚本
├── runtime/                    # 本地运行时（Git 忽略）
└── models/                     # 本地模型（Git 忽略）
training/                       # 数据、QLoRA 配置和评测
research/                       # 调研、训练与产品路线
```

## 隐私与许可证

聊天、设置和存档默认只保存在本机浏览器；应用服务器只监听 loopback。导出 JSON 前仍应自行检查是否含有不希望分享的私人对话。

项目自有代码和文档采用 [MIT License](LICENSE)。Free Sydney V2、KoboldCpp、Ollama、Qwen3 以及任何第三方素材分别遵循各自许可证和使用条款；它们不因被本项目调用而自动适用 MIT。
