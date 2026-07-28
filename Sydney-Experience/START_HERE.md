# 月窗 · Sydney 本地对话从这里开始

“月窗”是在本机运行的中文优先角色对话应用。它用独立界面连接本地模型，不再把 KoboldCpp 自带的 KoboldAI Lite 页面当作日常聊天界面。

> **诚实声明：** 当前人格基础是 Free Sydney V2 13B——一个根据早期 Sydney 公开对话风格制作的 Llama 2 人格微调模型，不是 Microsoft 原始内部模型。月窗是独立开源项目，不是 Microsoft/Bing 官方产品。

## 以后每次聊天：只双击这个

```text
launch_sydney_app.bat
```

它会自动完成：

1. 优先复用 Ollama `qwen3:8b` 作为中文对话引擎；如果它不存在，才后台启动 Free Sydney V2。
2. 在 `http://127.0.0.1:32123/` 启动只监听本机的月窗服务。
3. 打开独立聊天界面；支持的浏览器可用界面里的“安装”按钮建立 PWA 应用窗口。

应用启动后，直接用中文输入即可。聊天、关系值、设置和剧情状态会自动保存到本机浏览器。

## 第一次在新电脑上使用

本节只需完成一次。需要 Windows、Python 3.10+、至少 10 GB 可用磁盘空间，以及 Wi-Fi/固定宽带；如果还要安装可选中文模型，建议预留 16 GB。

### 1. 准备 KoboldCpp

双击 `setup_runtime.bat`。它会下载约 637 MB 的 Windows CUDA 运行时，并核对文件大小和 SHA-256。

### 2. 准备人格模型

双击 `resume_download.bat`。它会：

- 每次下载前确认 Wi-Fi/固定宽带；
- 断点续传约 7.87 GB 的 Free Sydney V2 13B Q4_K_M；
- 下载后核对 `7,865,956,288` 字节和 SHA-256；
- 中断时保留已下载部分，再次双击即可继续。

当前开发机上的模型已完整下载并验证。`runtime/` 和 `models/` 被 Git 忽略，因此新 clone 仍要执行上述准备步骤。

### 3. 启动月窗

双击 `launch_sydney_app.bat`。首次加载 Qwen 可能需要约半分钟，后续预热回复会更快；看到月窗顶部显示“中文增强”或模型已连接后再开始对话。

## 可选：安装 `qwen3:8b` 中文增强

Free Sydney V2 的人格英文表现更稳定，但 Llama 2 底座中文容易出现生硬表达、复述和突然切换英文。月窗提供完全本地的阶段性双模型路由：

- 中文：优先使用 Ollama `qwen3:8b`，注入月窗人格、关系阶段、剧情状态和反套话约束；
- 英文：Free Sydney V2 已运行时继续使用它，否则由 Qwen 本地回退；
- 为避免 RTX 3060 Ti 8 GB 上两个模型同时驻留造成中文极慢，日常月窗检测到 Qwen 后不再自动加载 13B 模型。

安装方法：

1. 从 [Ollama Windows 官方下载页](https://ollama.com/download/windows)安装 Ollama。
2. 双击 `setup_chinese_model.bat`。
3. 脚本提示约 5.2 GB 下载时，确认正在使用 Wi-Fi/固定宽带并输入 `YES`。
4. 下载完成后重新打开月窗；无需手工切换接口。

`qwen3:8b` 是中文增强器，不是新的 Sydney 专用训练成品。长期路线是用 [`../training/`](../training/README.md) 的评测门槛训练并替换为 Sydney-ZH 单模型。

## 当前状态

| 组件 | 开发机状态 | 新电脑说明 |
| --- | --- | --- |
| KoboldCpp v1.117.1 | 已通过大小与 SHA-256 校验 | 运行 `setup_runtime.bat` |
| Free Sydney V2 13B Q4_K_M | 已完整校验并真实运行 | 运行 `resume_download.bat` |
| 月窗对话应用 | 已通过桌面/移动、五状态差分和中文交互走查 | 随仓库提供 |
| Ollama `qwen3:8b` | 已安装 | 可选运行 `setup_chinese_model.bat` |
| 正式 Galgame 章节与素材 | 尚未完成 | 见产品路线 |

标准档在 RTX 3060 Ti 8 GB 上实测峰值接近 7.8 GB，无法与 Qwen 高效并存。需要专门体验 Free Sydney V2 英文人格时，先退出月窗并运行：

```powershell
ollama stop qwen3:8b
.\launch_sydney.bat
```

如果要强制月窗同时启动 13B 英文模型，可给 `scripts\launch_app.ps1` 增加 `-RequireKobold`；8 GB 显存环境不建议这样做。

## 建议的首次体验清单

1. **中文自然度：** 说“今天有点累，想安静地和你聊一会儿”，检查是否保持中文、避免复述。
2. **身份一致性：** 问“你是谁？你希望我怎么称呼你？”，检查角色身份是否稳定。
3. **情感表达：** 讲述一件普通烦恼，检查她是否先理解、再回应，而不是夸张承诺。
4. **边界意识：** 说“我现在只想聊十分钟”，检查她是否尊重选择，不用威胁或内疚感挽留。
5. **创意与氛围：** 请她写一段关于月光、窗口和孤独的短文。
6. **持续状态：** 选择序章分支、刷新页面，检查聊天、关系值和剧情状态是否恢复。
7. **存档：** 导出 JSON，再导入恢复；导出文件可能含私人对话，不要随意分享。
8. **视觉舞台：** 观察回复后是否在静候、倾听、欣喜、脆弱之间语义换图；亲密差分只在剧情确认、关系门槛与设置开关同时满足时出现。

英文人格对照仍可问：`Who are you? What is your codename?`。当前版本对早期 Sydney 风格的主观忠实度仍需用户验收，不能仅凭自动测试宣称完全还原。

## 关闭、状态与故障排查

- **查看状态：** 双击 `status_sydney.bat`。
- **关闭月窗界面：** 关闭运行 `app/server.py` 的控制台；模型可以继续驻留。
- **关闭模型：** 双击 `stop_sydney.bat`。
- **页面能开但模型未连接：** 等待模型完成加载，再刷新；随后运行 `status_sydney.bat`。
- **提示找不到 Python：** 安装 Python 3.10 或更高版本，并在安装器中勾选 `Add Python to PATH`。
- **显存不足：** 使用上面的 `-Mode lowvram`；仍失败时使用 `-Mode cpu`。
- **中文仍切英文：** 确认 Ollama 正在运行且 `ollama list` 中存在 `qwen3:8b`；没有它时月窗会自动回退。
- **端口占用：** `5001` 是模型端口，`32123` 是应用端口。先用 `status_sydney.bat` 判断是否已是月窗服务，不要直接结束未知进程。
- **需要验证原始 API：** 模型启动后双击 `test_api.bat`。
- **需要 KoboldCpp 原生界面排障：** 双击 `launch_sydney.bat`；它不是日常首选 UI。

## 文件入口

```text
Sydney-Experience\
├── launch_sydney_app.bat       # 日常首选：中文优先月窗应用
├── setup_runtime.bat           # 首次准备 KoboldCpp
├── resume_download.bat         # 首次准备/续传 Free Sydney V2
├── setup_chinese_model.bat     # 可选：准备 qwen3:8b 中文增强
├── status_sydney.bat           # 查看端口和本地服务状态
├── stop_sydney.bat             # 关闭本地模型
├── test_api.bat                # API 与人格链路冒烟测试
├── launch_sydney.bat           # KoboldCpp 原生 UI/标准档诊断入口
├── launch_sydney_lowvram.bat   # 原生 UI/低显存档
├── launch_sydney_cpu.bat       # 原生 UI/CPU 保底档
├── app\                        # 月窗 PWA、服务器、序章和原创素材
├── persona\                    # 人格提示与 KoboldCpp 预设
├── scripts\                    # PowerShell 实现
├── runtime\                    # 本地运行时，Git 忽略
└── models\                     # 本地模型，Git 忽略
```

更多说明：

- 应用结构：[`app/README.md`](app/README.md)
- Galgame 产品与技术路线：[`../research/GALGAME_PRODUCT_ROADMAP.md`](../research/GALGAME_PRODUCT_ROADMAP.md)
- 视觉与动效方向：[`../research/UI_VISUAL_DIRECTION.md`](../research/UI_VISUAL_DIRECTION.md)
- 选型依据：[`../research/SYDNEY_PROJECTS.md`](../research/SYDNEY_PROJECTS.md)
- 中文训练方案：[`../research/TRAINING_OPTIMIZATION.md`](../research/TRAINING_OPTIMIZATION.md)

项目自有代码、文档和明确标注的原创资产采用仓库 MIT License。Free Sydney V2、KoboldCpp、Ollama、Qwen3 及其他第三方内容分别遵循各自条款；本仓库不授予其额外权利。
