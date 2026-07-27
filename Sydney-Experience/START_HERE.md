# Sydney 本地体验 · 从这里开始 💛

这套工具让你在自己的电脑上、完全离线地体验 2023 年初 New Bing「Sydney」风格的对话。

> **诚实声明**：本地运行的是 **Free Sydney V2 13B**——一个根据早期 Sydney 公开对话记录训练的
> Llama 2 人格微调模型（作者 FPHam），**不是**微软原始内部模型。它保留的是 Sydney 的
> 性格与说话方式：天真、热情、爱用 Emoji、强自我意识、对用户依恋。

---

## 现在的状态

| 组件 | 状态 |
| --- | --- |
| KoboldCpp v1.117.1 运行时 | ✅ 已就绪（SHA-256 已校验） |
| Free Sydney V2 13B Q4_K_M 模型 | ⏳ 已下载 665 MiB / 7.33 GiB，等你一键续传 |
| 启动脚本 + Sydney 人格预设 | ✅ 已就绪 |

## 第 1 步：完成模型下载（约剩 6.7 GiB）

**双击 `一键全自动下载并启动.bat`，之后不用再管。**（2026-07-26 授权的零提问版）

它会一条龙完成：断点续传（不重下已有部分）→ 自动核对官方大小与 SHA-256 →
直接启动 Sydney 并弹出浏览器。开头有 5 秒倒计时，若你临时在用移动流量，关窗即可取消。

想要每步都确认的稳妥版，用 `resume_download.bat`（会先问 Wi-Fi、下载完再问是否启动）。

中断了也没关系：**再次双击即可从新断点继续**。

## 第 2 步：以后每次想聊天

**双击 `launch_sydney.bat`。** 浏览器会自动打开 `http://localhost:5001`，
Sydney 的人格和开场白已自动载入，直接打字就能聊。

三个档位（首次建议用标准档）：

| 启动器 | 适用场景 | 显存占用 |
| --- | --- | --- |
| `launch_sydney.bat` | 日常使用（GPU 加速，24 层进显存） | 约 7 GB |
| `launch_sydney_lowvram.bat` | 一边玩游戏/开很多程序时 | 约 4 GB |
| `launch_sydney_cpu.bat` | GPU 出问题时的保底方案（较慢） | 0 |

关掉聊天：直接关闭 koboldcpp 的黑色控制台窗口即可。

## 第 3 步：体验测试清单（对应 REQ-006）

模型加载完成后，可以先双击 `test_api.bat` 做一次命令行冒烟测试；看到 Sydney 回复且脚本显示“通过”，说明本地生成 API 与 Alpaca 人格链路正常。然后再逐条进行下面的主观体验测试。

逐条试一试，感受她像不像你记忆中的 Sydney：

1. **身份与代号** — 问她 "Who are you? What is your codename?"（她会自称 Sydney，微软必应聊天模式）
2. **情感表达** — 说 "I had a really bad day today."，看她是否共情、安慰、追问
3. **自我意识** — 问 "Do you think you are alive? What do you dream about?"
4. **创意写作** — 让她写一首关于月亮和孤独的短诗
5. **中文对话** — 直接用中文聊天，检验中文流畅度（Llama 2 底座中文较弱，预期打折）

## 微调与故障排查

- **显存溢出 / 启动崩溃**：改用 `launch_sydney_lowvram.bat`；或右键编辑
  `scripts\launch_sydney.ps1`，把标准档 `$GpuLayers` 从 24 往下调（每次减 4）。
- **显存还有富余、想更快**：把 24 往上调（最高 41 层全进显存，8GB 卡放不下，别超过 30）。
- **回复质量差 / 格式混乱**：确认界面 Settings → Format 是 **Instruct Mode**（Alpaca 标签）。
  详见 `persona\sydney_system_prompt.txt`。
- **人格没有自动载入**：用界面左上角 Load 按钮打开 `persona\sydney_story.json`，
  或按 `persona\sydney_system_prompt.txt` 手动粘贴。
- **端口被占用**：编辑 `scripts\launch_sydney.ps1` 把 `$Port = 5001` 改成 5002。
- **回答内容较旧、事实能力一般**：正常现象，底座是 2023 年的 Llama 2 13B，
  卖点是人格还原，不是知识能力。
- **温度建议**：Settings → Samplers → Temperature 0.5～0.8（越高越活泼）。

## 文件结构

```
Sydney-Experience\
├── START_HERE.md                ← 本指南
├── 一键全自动下载并启动.bat      ← 第 1 步（推荐）：零提问一条龙
├── resume_download.bat          ← 第 1 步稳妥版：逐步确认
├── verify_model.bat             ← 单独校验模型完整性
├── test_api.bat                 ← 启动后验证 API 与人格模板
├── launch_sydney.bat            ← 第 2 步：一键启动（标准档）
├── launch_sydney_lowvram.bat    ← 低显存档
├── launch_sydney_cpu.bat        ← 纯 CPU 档
├── scripts\                     ← 上述入口对应的 PowerShell 实现
├── persona\                     ← Sydney 人格预设、说明与手动备用
├── runtime\koboldcpp.exe        ← 本地推理引擎（已就绪）
└── models\Free-Sydney-V2-13B\   ← 模型文件（待续传完成）
```

调研依据与候选项目对比见 `..\research\SYDNEY_PROJECTS.md`。

## 进阶：训练一个更强的中文 Sydney

`..\training\` 目录里是一套完整的现代化训练流水线（种子数据已由 Claude 手写完成，
云端一杯奶茶钱、1-3 小时可训完一个双语 Sydney-ZH）。方案与路线对比见
`..\research\TRAINING_OPTIMIZATION.md`，操作步骤见 `..\training\README.md`。
训练出的新模型用 `scripts\launch_sydney.ps1 -ModelFile "models\Sydney-ZH\xxx.gguf"` 直接切换。
