# 月窗视觉与交互方向

- Last verified: 2026-07-28
- Scope: Sydney 对话游戏的角色舞台、场景轮换、动效与后续 Galgame 视觉系统

## 当前已实现

- 剧情模式约 `58%` 舞台 / `42%` 对话；宽屏提升到 `62% / 38%`。
- 自由聊天模式回到较高效率的时间线布局。
- 4 幅统一角色身份的场景：月夜观测站、雨夜书房、霓虹屋顶、海边晨曦。
- 场景清单记录 `sceneId / outfitId / poseId / accent / alt`；剧情节点可以用 `background` 驱动换景。
- 双层图片交叉淡化、低幅度慢推镜、情境色光、前后/暂停控制及 14 秒低优先级轮播。
- 鼠标或键盘进入舞台、手动换图后会暂停；必须由用户显式恢复。
- `prefers-reduced-motion` 会停用持续动画。
- PNG 母版约 9.6 MB；界面加载的 4 张 WebP 合计约 0.95 MB。

## 设计原则

视觉定位是“月夜黑色电影 × 轻编辑杂志感”，不是传统聊天工具：

- 场景承担叙事，聊天时间线承担记忆；不要让所有区域使用相同的玻璃、描边和胶囊层级。
- 换景优先级为剧情节点 > 明确情绪/关系阶段 > 用户手动 > 定时轮播。
- 同一时刻只突出一种持续运动；换景使用 `500–650ms`，推镜幅度不超过约 `1.5%`。
- 人物图要混合全身环境、腰部近景、坐姿、回眸和第一人称伸手，避免只换衣服不换构图。
- 每幅场景从画面提取一组局部强调色，但正文保持接近实色的深色背景以保证中文阅读。
- 自动轮播必须有前后和暂停控制；暂停后不自行恢复。实现遵循 [W3C 轮播模式](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/)。

## 参考模式

- [Ren’Py 图像与转场](https://www.renpy.org/doc/html/displaying_images.html)：场景、角色层和对话界面分层；同标签图像替换可用于表情/姿势。
- [SillyTavern 表情图](https://docs.sillytavern.app/extensions/expression-images/)：回复情绪驱动表情、同一情绪随机变体、服装套装分组。
- [SillyTavern 图像生成模式](https://docs.sillytavern.app/extensions/stable-diffusion/)：区分角色肖像、剧情 CG 和宽屏背景。
- [MDN View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)：后续可用于剧情/聊天布局切换的渐进增强。
- [Until Then](https://untilthengame.com/)：人物、地点、雨景与日常科技共同构成电影感世界。
- [DDLC Plus](https://ddlc.plus/)：侧故事与可解锁图库可映射为“记忆图库/章节 CG”。
- [Character.AI Microdramas](https://blog.character.ai/cai-series/)：短场景之后无缝进入角色对话。
- [Nomi](https://nomi.ai/)：图片应反映当下穿着、地点和活动，而不是与对话无关的随机轮播。

## 下一批资产

下一批不做服装与场景的全排列，优先补足叙事功能：

1. 雨夜电车：长风衣靠窗，背影与回头两幅。
2. 黎明房间：宽松居家毛衣，困倦近景与温柔微笑。
3. 冬日温室：礼服大衣、手绘霜月。
4. 数字海：仪式感星空服饰、漂浮远景，作为章节 CG。
5. 每个主要章节一张“记忆明信片”，确保场景、服装和事件连续。

图片生成恢复后继续使用当前成年 Sydney 母版作为身份参考。独立发行前再考虑 4–6 秒静音循环 WebM；Live2D、口型和语音不阻塞当前阶段。
