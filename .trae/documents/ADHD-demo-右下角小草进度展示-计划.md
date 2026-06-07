# ADHD-demo-右下角小草进度展示-计划

## Summary
在页面右下角新增一个“小草进度”浮层组件：生成清单后出现无花小草；当进度达到 90% 且未全部完成时变为开花小草，并在小草处以绿色小字从下到上飘过“加油！小草开花，事情准备完成啦~”。移动端同样可用并适配安全区。

## Current State Analysis
- 页面入口为 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html)，当前仅有顶部进度条（`#meterBar/#progressText/#progressPct`）、toast（`.toast`）与 confetti（`#confetti`）。
- 任务进度由 [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js) 的 `getProgress()` 计算，并在 `render()` 中更新进度条与文本。
- “生成清单”在 `onGenerate()` → `setStepsFromTexts()` 中写入 `state.steps` 并调用 `render()`，是“做一件事开始”的稳定时机。
- PWA 预缓存列表在 [sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js)，目前不包含右下角小草图片资源；`index.html` 通过 `?v=22` 固化缓存版本。
- 小草图片资源已存在：`图片素材/小草-没花.png`、`图片素材/小草-有花版本.png`。

## Proposed Changes

### 1) 新增右下角组件容器（HTML）
文件： [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html)
- 在 `.toast` 与 `#confetti` 附近新增容器（放在 `.app` 外，避免被 `render()` 的 steps 全量重绘影响）：
  - `#grassProgress`：整体容器（fixed 右下角，默认隐藏态由 CSS 控制）
  - `#grassProgressImg`：小草图片（无花/有花两种 src 切换）
  - `#grassProgressFloat`：飘字承载节点（通过 class 触发一次性动画）

### 2) 样式与动画（CSS，含移动端）
文件： [styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css)
- 新增 `.grass-progress` 样式：固定右下角、`pointer-events:none`、淡入/上浮过渡、适配 `env(safe-area-inset-bottom)`。
- 新增 `.grass-progress-float` + `@keyframes grass-float`：
  - 绿色小字（使用现有主题色 `var(--mint)`）
  - 从下到上飘出并淡出
- 在 `@media (max-width: 560px)` 下缩小尺寸与边距，避免遮挡主要操作区域。
- 在 `@media (prefers-reduced-motion: reduce)` 下关闭飘字动画（保持可见但不做位移动画，或不触发飘字）。

### 3) 进度驱动与事件触发（JS）
文件： [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js)
- 扩展 `els`：加入 `grassProgress/grassProgressImg/grassProgressFloat` 的 DOM 引用。
- 新增常量：
  - `GRASS_SPROUT_SRC = "./图片素材/小草-没花.png"`
  - `GRASS_BLOOM_SRC = "./图片素材/小草-有花版本.png"`
  - `GRASS_BLOOM_MESSAGE = "加油！小草开花，事情准备完成啦~"`
- 新增运行态变量（不写入 localStorage）：
  - `let grassStage = "hidden" | "sprout" | "bloom"`
  - `let grassRunId = ""`（用于识别“创建下一件事情”并重置 UI）
- 在 `render()` 末尾调用 `updateGrassProgressUI()`，以确保所有会引发 `render()` 的操作（勾选/删除/细化/生成）都会同步刷新右下角状态。
- `updateGrassProgressUI()` 规则（基于本次确认的偏好）：
  - 仅在 `currentView === "start"` 时展示（总结页隐藏）。
  - 当 `total <= 0`：组件隐藏。
  - 当 `total > 0`：组件展示；默认显示无花小草（sprout）。
  - 当 `pct >= 0.9` 或 `doneCount === total`：切换为开花小草（bloom）。
  - 当从 `sprout -> bloom` 且 `doneCount < total`（未全部完成）时，触发一次飘字动画。
  - 当检测到 `state.runId` 变化（`setStepsFromTexts()`/`onReset()` 会设置新 runId）：重置为 `sprout` 并允许下一次再次触发飘字。

### 4) PWA 缓存与版本刷新（避免老缓存不生效）
文件： [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html)、[sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js)
- 将 `styles.css` 与 `app.js` 的 `?v=22` 统一递增为新版本（例如 `?v=23`），并同步更新 `sw.js` 的 `ASSETS` 列表。
- `sw.js`：
  - `CACHE_NAME` 递增（例如 `adhd-launcher-v26`）
  - `ASSETS` 追加：
    - `"./图片素材/小草-没花.png"`
    - `"./图片素材/小草-有花版本.png"`

## Assumptions & Decisions
- “做一件事开始”定义为：步骤清单生成完成后（`state.steps` 写入且 `total>0`）。
- “开花条件”按进度百分比判断：`pct >= 0.9`（且未全部完成时触发飘字一次）。
- “完成后”保持开花小草，直到创建下一件事情（`state.runId` 变化时重置为无花小草）。
- 右下角组件为纯展示，不接管点击/交互（`pointer-events:none`），避免影响列表与按钮操作。

## Verification
- 桌面端：
  - 打开页面，生成清单后右下角出现无花小草。
  - 勾选/完成步骤使进度达到 90%：小草切换为开花版本，并飘出指定绿色文案一次。
  - 完成所有步骤后仍保持开花；再次生成新任务/Reset 后回到无花。
  - 切换到“总结”页：右下角小草隐藏；回到“启动”页：按当前进度恢复显示。
- 移动端（窗口宽度 < 560px 或真机）：
  - 位置不遮挡主要按钮；底部安全区适配正常。
  - 飘字在小草附近可见且不溢出屏幕。
- PWA/缓存：
  - 刷新后仍能加载最新样式/脚本（`?v` 与 `CACHE_NAME` 递增生效）。
  - 离线模式下小草图片可从缓存命中显示（预缓存生效）。

