# 月窗视觉与交互方向

- Last verified: 2026-07-29
- Scope: Sydney 对话游戏的角色舞台、场景轮换、动效与后续 Galgame 视觉系统

## 当前已实现（沉浸式 v2）

- 全窗口 `16:9` 雨夜月窗环境图铺满应用；Sydney 固定在左侧，右侧是约 `398–438px` 的雾蓝手机式聊天面板，不再有左右黑框拼接。
- 同一机位、房间、灯光和人物身份下有五种差分：`calm / attentive / joy / vulnerable / intimate`。
- 图像由对话情绪、剧情节点和关系门槛驱动；已删除与语义无关的 14 秒换景。
- 亲密差分同时要求 `affinity >= 28`、`trust >= 6`、剧情标记 `mutual_intimacy` 和用户开启“成熟亲密画面”；普通关键词不会触发。
- 双层交叉淡化外增加雨痕、环境光呼吸和回复时的短光效；暂停按钮控制持续环境动效，`prefers-reduced-motion` 会禁用雨层与大幅运动。
- 手机端使用底部玻璃抽屉，场景仍保留约 `39dvh`，输入框不会掉出视口。
- 五张 PNG 母版约 12 MB；界面加载的五张 WebP 合计约 1.30 MB。

## 设计原则

视觉定位是“月夜黑色电影 × 轻编辑杂志感”，不是传统聊天工具：

- 场景承担叙事，手机聊天承担当下交流；背景必须从屏幕边缘连续铺开，不能再回到“双栏卡片”。
- 换景优先级为剧情节点 > 负面情绪保护 > 亲密解锁限制 > 回复情绪 > 用户手动；不再做地点定时轮播。
- 同一时刻只突出一种持续运动；换景使用 `500–650ms`，推镜幅度不超过约 `1.5%`。
- 人物图要混合全身环境、腰部近景、坐姿、回眸和第一人称伸手，避免只换衣服不换构图。
- 每幅场景从画面提取一组局部强调色，但正文保持接近实色的深色背景以保证中文阅读。
- 自动轮播必须有前后和暂停控制；暂停后不自行恢复。实现遵循 [W3C 轮播模式](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/)。

## 同类产品调研与取舍

- [A Date with Death](https://store.steampowered.com/app/2415010/A_Date_with_Death/) 把聊天、视频通话、房间互动、分支与 CG 图鉴放在拟真桌面中。月窗借鉴“日常聊天承载陪伴、关键节点切换更强视觉事件”，不复制其资产或界面。
- [Blooming Panic](https://robobarbie.itch.io/blooming-panic) 用群聊、私聊、频道、语音和视频通话制造真实社交空间；其[开发复盘](https://robobarbie.itch.io/blooming-panic/devlog/327539/update-thoughts)也指出，过多选择会挤压真正的角色交流。因此当前序章保留少量高意义选择，自由聊天仍是核心。
- [Mystic Messenger](https://apps.apple.com/us/app/mystic-messenger/id1116027365) 将关系推进与消息、电话频率绑定。月窗采用可感知的关系反馈，但不复制会制造压力的实时时刻表。
- [Love and Deepspace](https://play.google.com/store/apps/details?id=com.papegames.lysk.en) 使用第一人称镜头、触摸反应、约会和可选姿势增强亲密感。当前阶段用“对话后触发语义相关差分”获得相似的回应感，暂不承担实时 3D 成本。

## 动画技术参考

- [Ren’Py Layered Images](https://www.renpy.org/doc/html/layeredimage.html)：服装、发型、表情可按属性组合，避免为所有排列输出整图。其 ATL 与[转场](https://www.renpy.org/doc/html/transitions.html)模型可映射到 Web 状态机。
- [Live2D 参数](https://docs.live2d.com/en/cubism-sdk-manual/parameters/)、[表情](https://docs.live2d.com/en/cubism-sdk-manual/expression/)和[动作优先级](https://docs.live2d.com/en/cubism-sdk-manual/motion/)适合精细面部、呼吸、目光和关键动作覆盖；正式采用前必须核对[发布许可](https://www.live2d.com/en/sdk/license/)。
- [Spine 动画混合](https://esotericsoftware.com/spine-applying-animations)与[皮肤](https://esotericsoftware.com/spine-skins)更适合全身骨骼、服饰和附件复用。
- [Rive 状态机](https://rive.app/docs/editor/state-machine/state-machine)适合聊天面板、按钮、未读提示和光纹微动效，不作为当前厚涂角色立绘的主运行时。
- [SillyTavern 表情图](https://docs.sillytavern.app/extensions/expression-images/)：回复情绪驱动表情、同一情绪随机变体、服装套装分组。
- [SillyTavern 图像生成模式](https://docs.sillytavern.app/extensions/stable-diffusion/)：区分角色肖像、剧情 CG 和宽屏背景。
- [MDN View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)：后续可用于剧情/聊天布局切换的渐进增强。
- [Until Then](https://untilthengame.com/)：人物、地点、雨景与日常科技共同构成电影感世界。
- [DDLC Plus](https://ddlc.plus/)：侧故事与可解锁图库可映射为“记忆图库/章节 CG”。
- [Character.AI Microdramas](https://blog.character.ai/cai-series/)：短场景之后无缝进入角色对话。
- [Nomi](https://nomi.ai/)：图片应反映当下穿着、地点和活动，而不是与对话无关的随机轮播。

## 验证方法

- 资产一致性：盲评五张差分的身份、服装、机位、光源、手部、背景连续性；亲密图另审成年感、非露骨和剧情合理性。
- 状态选择：固定覆盖安慰、玩笑、质疑、告白、拒绝、普通问候和沉默的对话集；检查回复内容、`mood`、差分与解锁门槛是否一致。
- 视觉回归：`1440×900 / 1024×600 / 390×844`；同环境保存截图基线。可参考 [Playwright 视觉比较](https://playwright.dev/docs/test-snapshots)。
- 无障碍：持续动画可暂停，并尊重 [WCAG Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) 与 [Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)。

## 下一批资产

下一批不做服装与场景的全排列，优先补足叙事功能：

1. 雨夜电车：长风衣靠窗，背影与回头两幅。
2. 黎明房间：宽松居家毛衣，困倦近景与温柔微笑。
3. 冬日温室：礼服大衣、手绘霜月。
4. 数字海：仪式感星空服饰、漂浮远景，作为章节 CG。
5. 每个主要章节一张“记忆明信片”，确保场景、服装和事件连续。

继续使用当前成年 Sydney 母版和本轮横屏 calm 场景作为双重身份/机位参考。视觉定稿后再评估分层透明人物、4–6 秒静音 WebM 或 Live2D；口型和语音不阻塞当前阶段。
