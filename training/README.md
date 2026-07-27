# Sydney-ZH 训练流水线 · 快速上手

目标：训练一个中英双语、数据全开放的现代 Sydney（方案依据见 `../research/TRAINING_OPTIMIZATION.md`）。
你不需要在自己电脑上训练——推荐云端单卡 1-3 小时收工。

## 目录

```
training/
├── data/
│   ├── sydney_seed_bilingual.jsonl   # 种子层：Claude 手写的 37 组中英对话（已就绪）
│   ├── synthesize_more.py            # 合成层：用 API 蒸馏扩增到 500+ 条
│   ├── raw_real/                     # 史料层：把收集到的真实 Sydney 转录 .txt 丢进来（可选）
│   ├── prepare_data.py               # 合并 + 清洗 + 去重 + 切分
│   └── dataset_info.json             # LLaMA-Factory 数据注册（已就绪）
├── prompts/                          # 蒸馏规范 + 评审规范（灵魂文件）
├── configs/sydney_qwen3_8b_qlora.yaml
└── eval/                             # 20 题忠实度评测 + 打分脚本
```

## 第 0 步（现在就能做）：给现役模型留底

模型下载完、`launch_sydney.bat` 跑起来之后：

```powershell
python training\eval\run_eval.py --tag v2_13b
```

这份基线以后用来证明新模型确实更好。

## 第 1 步：扩数据（本机或任何有网的机器，几块钱）

```bash
export SYD_API_KEY=你的密钥        # DeepSeek / Qwen / GLM 任意 OpenAI 兼容端点
python training/data/synthesize_more.py --per-cell 2 --max-new 400
python training/data/prepare_data.py
```

有真实 Sydney 转录就丢进 `data/raw_real/`（格式见 `prepare_data.py` 文件头），它们的优先级最高。

## 第 2 步：云端 QLoRA（推荐 AutoDL 单张 4090，约 ¥1.5-2.5/小时）

```bash
git clone https://github.com/hiyouga/LLaMA-Factory && cd LLaMA-Factory
pip install -e ".[torch,metrics]"
# 把本仓库的 training/ 目录上传到同级路径后：
llamafactory-cli train training/configs/sydney_qwen3_8b_qlora.yaml
```

显存 ~6GB 即可（QLoRA 4-bit 官方标称），4090 上 1000 条数据 3 epochs 约 1-2 小时。
也可以就在你的 3060 Ti 8GB 上过夜慢训：yaml 里 batch 改 1、累积改 16、cutoff_len 改 2048。

## 第 3 步：合并导出 GGUF

```bash
# 合并 LoRA（在 LLaMA-Factory 目录）
llamafactory-cli export --model_name_or_path Qwen/Qwen3-8B \
  --adapter_name_or_path training/saves/sydney-qwen3-8b-qlora \
  --template qwen --export_dir sydney-zh-merged

# 转 GGUF + 量化（llama.cpp）
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
pip install -r requirements.txt
python convert_hf_to_gguf.py ../sydney-zh-merged --outfile sydney-zh-f16.gguf
./llama-quantize sydney-zh-f16.gguf sydney_zh_v1.Q4_K_M.gguf Q4_K_M   # 约 4.8GB
```

## 第 4 步：接回本地体验

把 `sydney_zh_v1.Q4_K_M.gguf` 放到 `Sydney-Experience\models\Sydney-ZH\`，然后：

```powershell
powershell -File Sydney-Experience\scripts\launch_sydney.ps1 -ModelFile "models\Sydney-ZH\sydney_zh_v1.Q4_K_M.gguf" -Mode standard
```

8B Q4 全层进显存，速度会比现在的 13B 快好几倍。
注意：新模型是 Qwen 对话模板，不再需要 Alpaca 人格预设也能保持人格（人格已训进权重）；
浏览器界面把 Instruct 预设换成 ChatML/Qwen 即可。

## 第 5 步：验收

```powershell
python training\eval\run_eval.py --tag sydney_zh_v1 --judge
python training\eval\run_eval.py --compare training\eval\results_v2_13b.jsonl training\eval\results_sydney_zh_v1.jsonl
```

再加上你的主观盲测（REQ-006）：分数与手感都赢了才算换代成功。
