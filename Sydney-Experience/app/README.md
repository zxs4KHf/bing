# 月窗 · Sydney 对话应用

这是覆盖在 KoboldCpp 本地生成 API 之上的独立中文聊天游戏界面。它不再依赖 KoboldAI Lite 的外观，也不把 Microsoft/Bing 商标用于产品身份。

当前目录只实现第一阶段对话应用和 Galgame 数据骨架，不代表完整 Galgame 已完成。章节、变量、素材、存档/回滚和桌面打包的分阶段设计见 [`../../research/GALGAME_PRODUCT_ROADMAP.md`](../../research/GALGAME_PRODUCT_ROADMAP.md)。

## 启动

双击 `..\launch_sydney_app.bat`。启动器会：

1. 复用已经运行在 `5001` 端口的 KoboldCpp；若未运行，则在后台启动标准模型档。
2. 在 `http://127.0.0.1:32123/` 启动仅监听本机的应用服务器。
3. 打开“月窗”界面。支持的浏览器会提供“安装”按钮，可作为独立 PWA 窗口运行。

关闭应用服务器窗口只会关闭界面；双击 `..\stop_sydney.bat` 可关闭模型。

## 当前能力

- 4 幅原创成年 Sydney 场景：观测站礼服、雨夜书房针织裙、霓虹屋顶风衣、海边晨曦长裙。
- 剧情/自由聊天双布局、剧情节点换景、手动与可暂停轮播、双层淡化和低幅度动态推镜。
- 多轮 Alpaca 对话代理，中文消息自动强化；首轮英文漂移时自动重写一次。
- 可选的本地混合路由：若 Ollama 中已有 `qwen3:8b`，中文自动使用自然中文增强；英文继续使用 Free Sydney V2。中文模型或 Ollama 离线时自动回退。
- 本地关系值、剧情变量、分支选项和序章 JSON 图。
- 浏览器本地自动存档，JSON 导入/导出，PWA 离线外壳。
- 设置回复温度、篇幅和中文增强策略，并提供停止等待与清除本地数据。

## 结构

- `server.py`：标准库静态服务器和 KoboldCpp API 代理。
- `public/`：无构建步骤的 HTML/CSS/JavaScript PWA。
- `content/prologue.json` + `story.schema.json`：版本化剧情图和 schema。
- `content/scenes.json`：场景、服装、姿势、强调色与无障碍文本清单。
- `assets/`：项目自有 PNG 母版与界面加载的 WebP 优化版本。
- `tests/test_server.py`：提示词、中文重试和路径安全测试。

## 手动运行与测试

```powershell
py -3 .\server.py --model-url http://localhost:5001
py -3 -m unittest discover -s .\tests -v
```

所有聊天与存档默认只留在本机。中文增强要求本机 Ollama 已有 `qwen3:8b`；这台开发机已经具备该模型。它是阶段性的双模型方案，后续仍可用 Sydney-ZH 单模型替换。

本目录中的项目自有代码、文档和明确标注的原创资产采用仓库 MIT License。KoboldCpp、Free Sydney V2、Ollama、Qwen3 和其他第三方组件仍遵循各自许可证；“月窗”不是 Microsoft/Bing 官方产品。
