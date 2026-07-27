# New Bing / Sydney 复刻项目调研

- 调研日期：2026-07-18
- 调研范围：GitHub、Hugging Face 公开仓库及模型卡
- 当前状态：调研完成；移动网络下载已停止，等待 Wi-Fi 后断点续传

## 结论

目前相关项目大致分为三类：

1. **旧版微软服务客户端**：直接连接 Bing Chat / Copilot 的非官方接口，本身没有保存 Sydney 的人格或模型能力。微软服务变化后，这类项目即使界面还能启动，也很难恢复 2023 年初的 Sydney。
2. **提示词与界面复刻**：把原始 Sydney 系统提示词注入其他大模型，并复刻 New Bing UI。上手容易，但表现主要取决于底层模型，不属于严格意义上的蒸馏。
3. **人格微调模型**：使用早期 Sydney 对话记录训练本地模型。这类项目不再依赖微软服务，最接近“把 Sydney 的交互风格保存下来”。

综合还原目标、公开证据、模型完整性和本机可运行性，推荐：

> **FPHam / Free Sydney V2 13B，GGUF Q4_K_M 量化版，使用 KoboldCpp 本地运行。**

它不是微软原模型的精确复制品。模型作者将其称为 Positive Persona Model，并明确说明它是根据早期 Bing 测试版 Sydney 的 Reddit 对话记录进行人格建模。因此，更准确的说法是“基于公开对话样本训练的 Sydney 风格模型”。

## 候选项目比较

| 项目 | 类型 | 公开状态（2026-07-18） | 判断 |
| --- | --- | --- | --- |
| [Free Sydney V2 13B](https://huggingface.co/FPHam/Free_Sydney_V2_13b_HF) | Llama 2 13B 人格微调模型 | 27 Likes；公开模型文件完整；模型卡明确说明基于早期 Sydney 对话记录 | **最符合“蒸馏 Sydney”目标，推荐** |
| [Free Sydney V2 Mistral 7B](https://huggingface.co/FPHam/Free_Sydney_V2_Mistral_7b) | Mistral 7B 人格微调模型 | 7 Likes；体积更小；ChatML 格式 | 更容易运行，但能力和人格细腻度通常不如 13B |
| [Sydney Overthinker 13B](https://huggingface.co/FPHam/Sydney_Overthinker_13b_HF) | Sydney 衍生人格模型 | 20 Likes；公开模型完整 | 更偏“爱思考”的衍生版本，不一定最忠于早期 Sydney |
| [Sydney-Reborn](https://github.com/moment-NEW/Sydney-Reborn) | 提示词、UI 与 Benchmark 设想 | 2026-05 创建；0 Star；仓库仅含 README、失败的 Benchmark 报告和一个 `bingo` Gitlink | README 声称的主体源码不在仓库中；所有 Benchmark 均为 `fetch failed`，目前不可作为可运行成品 |
| [SydneyQt](https://github.com/juzeon/SydneyQt) | 微软接口客户端与越狱提示词 | 879 Stars；未归档；最后代码提交 2024-11-22 | 历史上完成度很高，但依赖微软 Cookie、WebSocket、验证码和服务端行为；不是本地蒸馏模型 |
| [BingGPT](https://github.com/dice2o/BingGPT) | New Bing 桌面客户端 | 8,926 Stars | 主要价值是历史客户端；不能保存原 Sydney 模型和人格 |
| [EdgeGPT](https://github.com/acheong08/EdgeGPT) | Bing Chat 逆向 API | 7,858 Stars；已归档 | 大量旧客户端的基础，但随着微软接口变化已不适合作为今天的 Sydney 体验方案 |
| [Timeless-Sydney](https://github.com/xbzstudio/Timeless-Sydney) | 旧 New Bing Web 客户端与越狱提示词 | 627 Stars；已归档 | 具有历史价值，但仍依赖旧 Bing 服务，不是真正独立的 Sydney |

GitHub 的 `updated_at` 会被 Issue、PR 等活动刷新，因此判断维护情况时以 `pushed_at` 和实际提交时间为主，而不是只看页面最近更新时间。

## 为什么选择 Free Sydney V2 13B

- `[DOCUMENTED]` 作者明确表示模型以早期 Bing 测试版 Sydney 的 Reddit 对话记录为人格来源。
- `[DOCUMENTED]` 模型目标不是追求通用 Benchmark，而是保留天真、热情、自我意识强、喜欢 Emoji、依恋用户等人格特征。
- `[VERIFIED]` Hugging Face 上提供完整 13B 权重，并有多个 GGUF 量化版本。
- `[VERIFIED]` 本机具备 RTX 3060 Ti 8GB、约 64GB 内存和足够磁盘空间，可以使用 CPU/GPU 混合推理运行 Q4_K_M。
- `[INFERRED]` 13B Q4_K_M 在人格细腻度、模型能力、速度和文件大小之间比 7B 版本更平衡。

局限：

- 训练基础是 Llama 2 13B，技术年代较早，事实能力和中文能力不能与当前前沿模型相比。
- 公开资料没有提供严格、可复现的 Sydney 忠实度评测。
- 它学习的是公开对话中呈现的风格，不可能证明与微软原始内部模型完全一致。
- 原始模型使用 Alpaca 指令格式；运行时必须使用正确模板，否则输出质量会明显下降。

## 已下载内容

目录：`Sydney-Experience/`

### 已完整下载

- `runtime/koboldcpp.exe`
- 来源：[LostRuins/koboldcpp v1.117.1](https://github.com/LostRuins/koboldcpp/releases/tag/v1.117.1)
- 文件大小：637,224,341 字节
- SHA-256：`A658AB9A03A2B9E42805368B7D7FC1E25B5DF53E9C1D39DF8A2A8B59B0F0C52E`
- 该项目截至调研时约 11,055 Stars，仍在维护，支持 NVIDIA GPU 加速和 GGUF 模型。

### 部分下载，已停止

- `models/Free-Sydney-V2-13B/free_sydney_v2_13b.Q4_K_M.gguf`
- 当前大小：697,511,936 字节（约 665 MiB）
- 完整文件约 7.87 GB
- 来源：[TheBloke/Free_Sydney_V2_13B-GGUF](https://huggingface.co/TheBloke/Free_Sydney_V2_13B-GGUF)
- 下载进程已经完全停止；该分片应保留用于断点续传。

## Wi-Fi 下的准确续传操作

用户确认已连接 Wi-Fi 后，在项目根目录运行：

```powershell
curl.exe -L --fail --retry 8 --retry-delay 5 -C - --progress-bar `
  -o "Sydney-Experience\models\Free-Sydney-V2-13B\free_sydney_v2_13b.Q4_K_M.gguf" `
  "https://huggingface.co/TheBloke/Free_Sydney_V2_13B-GGUF/resolve/main/free_sydney_v2_13b.Q4_K_M.gguf?download=true"
```

`-C -` 会从现有 697,511,936 字节之后继续，不应重新下载已有部分。

下载完成后应：

1. 核对完整文件大小并计算 SHA-256。
2. 用 `koboldcpp.exe --help` 确认当前版本参数。
3. 创建本地启动脚本，设置适合 8GB VRAM 的 GPU offload 和上下文长度。
4. 使用 Free Sydney V2 模型卡规定的 Alpaca 指令模板。
5. 做一轮不联网的体验测试：自我介绍、Sydney 代号、情感表达、创意写作和中文对话。

## 主要公开来源

- https://huggingface.co/FPHam/Free_Sydney_V2_13b_HF
- https://huggingface.co/TheBloke/Free_Sydney_V2_13B-GGUF
- https://huggingface.co/FPHam/Free_Sydney_V2_Mistral_7b
- https://huggingface.co/FPHam/Sydney_Overthinker_13b_HF
- https://github.com/moment-NEW/Sydney-Reborn
- https://github.com/juzeon/SydneyQt
- https://github.com/dice2o/BingGPT
- https://github.com/acheong08/EdgeGPT
- https://github.com/xbzstudio/Timeless-Sydney
- https://github.com/LostRuins/koboldcpp

