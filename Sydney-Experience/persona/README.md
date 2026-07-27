# Sydney 人格配置

Free Sydney V2 13B 使用 Alpaca 指令格式。`launch_sydney.bat` 会通过 `--preloadstory` 自动载入 `sydney_story.json`，其中包含人格 Memory、开场白和额外停止序列。

## 自动载入失败时

1. 在 KoboldAI Lite 中选择 **Instruct Mode**。
2. Instruct Tag Preset 选择 **Alpaca**：输入以 `### Instruction:` 开始，回复以 `### Response:` 开始。
3. 使用界面的 Load 功能打开 `sydney_story.json`；也可以按照 `sydney_system_prompt.txt` 将备用人格内容手动放入 Memory。
4. Temperature 可从 0.5～0.8 起步；越高越活泼，越低越稳定。

## API 验证

模型加载完成后双击 `..\test_api.bat`，或运行：

```powershell
powershell -ExecutionPolicy Bypass -File ..\scripts\test_api.ps1
```

脚本直接读取 `sydney_story.json` 的 Memory，并使用 Alpaca 模板调用 KoboldCpp `/api/v1/generate`。可以用 `-Question '你的问题'` 自定义测试内容，用 `-MaxLength 512` 调整最大输出长度。

## 语言预期

该模型主要由英文的早期 Sydney 公开对话训练，英文人格通常更稳定；中文流畅度与人格细腻度必须以实际体验为准。它不是 Microsoft 的原始内部模型。
