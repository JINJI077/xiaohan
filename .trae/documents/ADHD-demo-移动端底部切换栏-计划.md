## Summary

在移动端（视口宽度 ≤ 560px）时，将顶部居中的“启动 / 总结”切换栏移动到页面底部居中；同时把 toast 提示改为顶部出现，避免与底部切换栏冲突。

## Current State Analysis

- 切换栏元素位于 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html#L17-L23)：
  - `<nav class="view-switch" id="viewSwitch"> ... </nav>`
- 切换栏当前样式在 [styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css#L80-L145)：
  - `position: fixed; top: calc(14px + env(safe-area-inset-top)); left: 50%; transform: translateX(-50%);`
- 移动端断点已存在：`@media (max-width: 560px)`，当前仅调整 `.app` 等布局，并未覆盖 `.view-switch` 位置。
- toast 当前是底部居中浮层：[styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css#L983-L1003)，移动端断点内也只是加入 safe-area-bottom，不改变其“底部出现”的逻辑。
- 切换栏指示器的定位逻辑基于 `getBoundingClientRect()`，并监听 `resize`，因此切换栏从顶部挪到底部不需要改 JS：[app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js#L141-L207)。

## Proposed Changes

### 1) 移动端将切换栏固定到底部

**File:** [styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css)

在 `@media (max-width: 560px)` 内新增/覆盖：
- `.view-switch`
  - `top: auto;`
  - `bottom: calc(14px + env(safe-area-inset-bottom));`
  - 保持 `left: 50%` 与 `transform: translateX(-50%)` 不变
- `.app`
  - 增加底部内边距以避让切换栏（包含 safe-area）：例如 `padding-bottom: calc(92px + env(safe-area-inset-bottom))`
  - 保持已有 `padding-top: calc(16px + env(safe-area-inset-top))`，避免内容贴顶

### 2) toast 在移动端改为顶部出现

**File:** [styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css)

在 `@media (max-width: 560px)` 内新增/覆盖：
- `.toast`
  - `bottom: auto;`
  - `top: calc(14px + env(safe-area-inset-top));`
  - 初始位移改为向上：`transform: translateX(-50%) translateY(-18px);`
- `.toast.is-show`
  - `transform: translateX(-50%) translateY(0);`
- 视需要补充 `z-index`（例如 80），确保 toast 不被卡片/背景遮盖

### 3) 更新离线缓存版本（避免旧 CSS 被 SW 命中）

**Files:**
- [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html)
- [sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js)

变更方式：
- 将 `styles.css?v=26`、`app.js?v=26` bump 到新版本号（例如 `v=27`）
- 将 `CACHE_NAME = "adhd-launcher-v29"` bump（例如 `v30`）
- 同步更新 `ASSETS` 列表中的 `styles.css` / `app.js` query 参数，与 `index.html` 一致

## Assumptions & Decisions

- “手机版”按用户选择定义为：`@media (max-width: 560px)`（与现有移动端断点一致）。
- toast 在移动端改为顶部出现（用户选择），桌面端保持现状。
- 不改动 `app.js` 的切换逻辑与指示器动画，仅通过 CSS 完成布局适配。

## Verification Steps

- 桌面宽度（> 560px）：
  - 切换栏仍位于顶部居中；点击/hover 指示器动画正常。
  - toast 仍在底部出现。
- 移动端宽度（≤ 560px）：
  - 切换栏固定在底部居中，且不遮挡卡片内容（滚动到页面底部也不会被覆盖）。
  - toast 在顶部出现，显示/隐藏动画方向正确。
- 进行一次强刷新或重新安装 PWA 后，确认加载到新 `styles.css?v=27` 并且 SW 缓存名更新。

