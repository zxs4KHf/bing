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

- 同一雨夜月窗机位的 5 幅原创成年 Sydney 差分：安静、倾听、喜悦、脆弱和受剧情/关系/用户开关共同约束的非裸露亲密状态。
- 全窗口场景、右侧手机聊天、剧情/自由聊天双布局、语义换景、手动轮切、双层淡化和可暂停环境动效。
- 中文流式回复会逐块显示；点击“停止”会断开浏览器请求并关闭正在运行的 Ollama 上游生成，取消后可立即开始下一次请求。
- 本地混合路由：若 Ollama 中已有 `qwen3:8b`，中文优先使用自然中文增强；英文在 Free Sydney V2 已运行时使用该模型，否则回退到本机 Qwen，避免 8 GB 显存争抢。
- 本地关系值、剧情变量、分支选项和序章 JSON 图。
- 浏览器本地自动存档、JSON 导入/导出和 PWA 离线外壳；v1 存档会自动迁移到 v2。
- 用户可显式把某条自己的消息加入长期记忆；记忆跨刷新和新会话保留，可在设置中逐条审阅、删除或清空，并受严格条数/字符预算与提示注入隔离规则约束。
- 设置回复温度、篇幅、中文增强和成熟画面策略，并提供清除本地数据；对话和长期记忆均为本机明文数据。

## 结构

- `server.py`：标准库静态服务器和 KoboldCpp API 代理。
- `public/`：无构建步骤的 HTML/CSS/JavaScript PWA。
- `content/prologue.json` + `story.schema.json`：版本化剧情图和 schema。
- `content/scenes.json`：场景、服装、姿势、强调色与无障碍文本清单。
- `assets/`：项目自有 PNG 母版与界面加载的 WebP 优化版本。
- `tests/test_server.py`：提示词、中文重试、流式事件/取消、长期记忆边界和路径安全测试。

## 手动运行与测试

```powershell
py -3 .\server.py --model-url http://localhost:5001
py -3 -m unittest discover -s .\tests -v
```

所有聊天与存档默认只留在本机。中文增强要求本机 Ollama 已有 `qwen3:8b`；这台开发机已经具备该模型。它是阶段性的双模型方案，后续仍可用 Sydney-ZH 单模型替换。

本目录中的项目自有代码、文档和明确标注的原创资产采用仓库 MIT License。KoboldCpp、Free Sydney V2、Ollama、Qwen3 和其他第三方组件仍遵循各自许可证；“月窗”不是 Microsoft/Bing 官方产品。
