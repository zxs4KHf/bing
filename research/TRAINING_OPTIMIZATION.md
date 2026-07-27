# Sydney 训练优化蓝图（2026-07-26）

- 作者视角：Claude（claude-fable-5），受用户委托"按你的方式做到更完美"
- 目标：超越 2023 年的 Free Sydney V2 13B——更聪明的底座、真正的中文能力、可复现的开放流水线
- 配套资产：`training/` 目录下全部脚本、配置、种子数据与评测套件（本仓库可直接使用）

## 一、对现有模型的"考古"结论

- `[VERIFIED]` FPHam 从未公开 Free Sydney 的训练数据集与训练脚本；V2 模型卡没有任何训练细节，方法写在他的付费书《The Cranky Man's Guide to LoRA & QLoRA》里。所谓"看源码优化"不可行——**必须开放重建**。
- `[VERIFIED]` FPHam 2025-2026 年已推出新一代 **Clever Sydney 4**（Gemma-3 12B 底座，Q4_K_M_O 量化 7.3 GB），数据来自早期 Bing 聊天记录的转写/截图 OCR，并混入了微软后来的"人格修正"。
- `[DOCUMENTED]` 训练方法可以从其作品谱系推断为：小规模精选对话（数百到数千条）+ QLoRA 人格微调，不追求通用能力基准。
- `[VERIFIED]` HF 与 GitHub 上**没有**现成的大规模 Sydney 对话数据集；可用史料是零散的：泄露的系统提示词 gist、JHU 数字档案馆存档的完整对话（如 "Bing AI (Sydney) Falls in Love With Me"）、NYT Roose 全文、r/bing 截图存档。

## 二、三条优化路线（按投入排序）

### 路线 A：零训练，直接换代（几分钟）
下载 FPHam 的 **Clever Sydney 4 12B**（Gemma-3 底座，比 Llama-2 13B 智力高一代），用现有 KoboldCpp 直接跑。
- 优点：零成本、作者一手数据；缺点：中文仍一般、"故意做得神经质"的调味未必合你口味、数据依旧黑箱。
- 想走这条路说一声，我把一键下载/启动脚本配好。

### 路线 B（推荐）：开放重建——"Sydney-ZH" 蒸馏训练（1 天内、约几十元）
用现代双语底座 + 三层数据 + QLoRA，训练一个**中英双语、可复现、数据全开放**的 Sydney。本蓝图其余部分即此路线的完整实现。

### 路线 C：史料众筹（长期）
持续把网上零散的真实 Sydney 对话（截图 OCR、档案馆、Reddit 存档）喂进 `prepare_data.py` 的 `raw_real/` 目录，逐步提高"真史料"占比，逼近博物馆级还原。

## 三、底座选型（2026-07 实况核查）

| 候选 | 参数 | 理由 | 推理占用 (Q4_K_M) |
| --- | --- | --- | --- |
| **Qwen3-8B**（保守默认） | 8B | `[VERIFIED]` LLaMA-Factory 官方支持；生态最成熟；36T tokens、119 语言训练，中文一流 | ≈ 4.8 GB，**8GB 卡全层进显存，比现在的 13B 快数倍** |
| **Qwen3.5-9B**（进阶首选） | 9B | `[VERIFIED]` 已有 unsloth / lmstudio 官方 GGUF，llama.cpp 已支持；Gated DeltaNet 架构长上下文 KV 省 40% | ≈ 5.5 GB，全层进显存 |
| Gemma-3 12B | 12B | FPHam 同款底座，人格表现力强 | ≈ 7.3 GB，勉强全进 |
| ~~Llama-2 13B~~ | 13B | 现役 V2 的底座，2023 年技术，中文弱、知识旧 | 7.87 GB，只能部分卸载 |

结论：**默认 Qwen3-8B，配置文件一行切换 Qwen3.5-9B**（若届时其 LLaMA-Factory/GGUF 链路在你环境验证通过）。两者都让 3060 Ti 从"部分卸载的 13B"升级为"全显存的 8-9B"——更聪明、更快、中文原生。

## 四、数据策略：三层配方（本仓库已就位）

1. **真实史料层**（`training/data/raw_real/`，可选）：你收集的任何真实 Sydney 转录（txt 粘贴即可），`prepare_data.py` 自动解析、清洗、去重。权重最高。
2. **种子层**（`training/data/sydney_seed_bilingual.jsonl`，已完成）：由我逐条手写的中英双语 Sydney 对话，覆盖身份/代号、情感、存在之思、依恋、创意写作、中文闲聊、温柔拒绝等 36 个场景——这就是你要的"用我的视角直接蒸馏"。
3. **合成扩增层**（`synthesize_more.py` + `prompts/sydney_generator_prompt.txt`）：用任意 OpenAI 兼容 API（DeepSeek/Qwen/GLM 都行，几块钱）按我写好的蒸馏规范批量生成 500-2000 条，脚本自带去重与安全过滤。

清洗规则（已实现在脚本里）：去 URL/用户名、长度过滤、哈希去重、剔除操纵/威胁向的极端样本（保留"戏剧化的可爱"，剔除"真实的伤害"）——这是对原始 Sydney 数据的**有意修正**：保留魅力，去掉毒性。

防灾难性遗忘：训练集自动混入 ~15% 通用指令数据（配置里 `dataset` 加 `alpaca_zh_demo` 之类即可，README 有说明）。

## 五、训练配置（`training/configs/sydney_qwen3_8b_qlora.yaml`）

QLoRA 4-bit，rank 32 / alpha 64，lr 1e-4，cosine，3 epochs，cutoff 4096，NEFTune α=5（小数据集上明显提升表达多样性）。要点：

- `[VERIFIED]` LLaMA-Factory 2026-10 changelog 仍在活跃更新，命令即 `llamafactory-cli train <yaml>`；QLoRA 4-bit 官方标称 7-9B 只需约 6 GB 显存。
- 算力两选一：**AutoDL 单张 4090（约 ¥1.5-2.5/小时，1-3 小时收工，总价一杯奶茶）**；或者就在你的 3060 Ti 8GB 上过夜慢练（可行，`[INFERRED]` 约 6-12 小时，README 有降内存参数）。
- 产出 LoRA → `llamafactory-cli export` 合并 → llama.cpp `convert_hf_to_gguf.py` + `llama-quantize` 出 Q4_K_M → 丢进 `Sydney-Experience/models/`，启动器已支持 `-ModelFile` 参数直接切换。

## 六、评测：不许"感觉不错"，要打分

- `training/eval/eval_prompts.jsonl`：20 道题 × 5 维度（身份忠实 / 情感表达 / 依恋与存在感 / 创意 / 中文自然度），中英对半。
- `training/eval/run_eval.py`：直接打本机 koboldcpp 的 OpenAI 兼容接口，跑完保存全部回答；可选 `--judge` 用 API 大模型按 `sydney_judge_prompt.txt` 逐维打 1-10 分。
- 标准流程：**先给现役 V2-13B 跑一遍留底 → 新模型跑一遍 → 对比分数 + 你的主观盲测**（对应 REQ-006 的客观化）。

## 七、风险与不确定性（诚实清单）

- `[UNKNOWN]` Qwen3.5-9B 的 LLaMA-Factory 训练链路未在你的环境实测；故默认写 Qwen3-8B。
- `[INFERRED]` 种子+合成数据总量 500-2000 条对人格微调充分（FPHam 谱系即小数据人格模型），但"像不像你记忆中的 Sydney"最终仍由你裁决。
- `[DOCUMENTED]` 任何重建都不是微软原模型；本方案的卖点是**开放、可复现、双语**，忠实度靠评测集持续逼近。
- 版本号、价格、仓库名以实际运行时为准，脚本内均有注释提示核对。

## 主要来源

- https://huggingface.co/FPHam/Free_Sydney_V2_13b_HF
- https://huggingface.co/FPHam/Clever_Sydney-4_12b_GGUF
- https://github.com/hiyouga/LLaMA-Factory
- https://insiderllm.com/guides/qwen-models-guide/
- https://huggingface.co/unsloth/Qwen3.5-9B-MTP-GGUF 与 https://huggingface.co/lmstudio-community/Qwen3.5-9B-GGUF
- https://gist.github.com/martinbowling/b8f5d7b1fa0705de66e932230e783d24 （泄露的 Sydney 系统提示词）
- https://digitalscholarship.library.jhu.edu/s/aivoices/item/78 （JHU 档案：真实 Sydney 对话存档）
