## Summary

聚焦重做“总结”界面：移除当前总结页占位元素，改为顶部居中大标题「🎉你已经成功完成 x 件事情，恭喜！🎉」，其中 x 随“完成一个大任务”的次数动态变化；下方以“相册时间轴”方式展示每次完成的大任务，按日期分组，卡片左上角始终显示完成时间（HH:mm），卡片主体显示任务名。

## Current State Analysis

- 项目为原生 HTML/CSS/JS 单页，无路由框架：[index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html)
- 目前已存在顶部“启动 / 总结”切换栏，`viewSummary` 是第二张 card（当前为占位）：[index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html#L118-L132)
- “完成全部步骤”的判定在勾选步骤时触发：`doneCount === total` 会 toast + `launchConfetti()`：[toggleStep](file:///d:/Github_Try/xiaohan/adhd-demo/app.js#L459-L484)
- 本地持久化只有 `taskText / steps / settings`，存储在 `localStorage[STORAGE_KEY]`：[loadState/saveState](file:///d:/Github_Try/xiaohan/adhd-demo/app.js#L1128-L1163)
- PWA 通过 Service Worker 预缓存 `styles.css?v=17`、`app.js?v=17`，改动后需 bump 版本避免旧缓存命中：[sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js#L1-L3)

## Assumptions & Decisions

- “事情”的计数口径：**完成一个大任务**（即某个任务的清单步骤全部勾选完成）记为 1 件。（用户已确认）
- 总结页卡片内容：**任务名 + 完成时间**。（用户已确认）
- 同一天多件时的时间戳策略：卡片左上角**始终显示**时间（HH:mm）。（用户已确认）
- 本次仅实现：记录完成历史 + 总结页 UI 渲染；不做“点击卡片回放/恢复任务”“删除单条记录”“云同步”等扩展功能（后续可迭代）。

## Proposed Changes

### 1) 数据：记录“完成的大任务”历史（localStorage 扩展）

修改 [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js)：

- 扩展存储 payload（保持向后兼容）：
  - 新增 `history`：完成事件数组（最新在前或后续渲染时排序）
  - 新增 `runId` / `runCompleted`：用于避免“反复勾选最后一步”造成重复记录
- 完成事件结构（示例）：
  - `{ id, taskText, completedAt, totalSteps }`
  - `completedAt` 使用 `new Date().toISOString()`，展示时按浏览器本地时区格式化
  - `id` 可用现有 `makeId()`
- 记录时机：
  - 在 `toggleStep()` 达成 `doneCount === total` 后，调用 `recordCompletionIfNeeded()`
  - 当生成新清单（`setStepsFromTexts`）或重置（`onReset`）时，更新 `runId` 并清空 `runCompleted`
- 数据上限：
  - 设置最大历史条数（例如 200），超出则截断最旧记录，避免 localStorage 无限增长
- `loadState()` 兼容旧数据：
  - 若 `history` 不存在则默认为 `[]`
  - 若 `runId/runCompleted` 不存在则生成默认值

### 2) 结构：重做“总结”界面 DOM（删掉占位元素）

修改 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html) 中 `#viewSummary`：

- 删除当前 `<header class="header">...` 和 `.summary-placeholder` 占位块
- 替换为：
  - 顶部 hero（居中大字）：
    - 文案：左右各一个礼花 emoji，中间为「你已经成功完成 x 件事情，恭喜！」
    - `x` 用 `<span id="summaryCount">0</span>` 由 JS 注入
  - 下方时间轴容器：
    - `<div id="summaryTimeline"></div>` 作为渲染挂载点
    - 空态：当没有历史时显示提示（例如“完成第一个大任务后，这里会出现相册一样的记录”）

### 3) 样式：相册式时间轴（延续现有设计语言）

修改 [styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css)：

- Hero 标题：
  - `.summary-hero`：居中、较大字号、适配移动端换行、emoji 与文字间距自然
  - 让 `x`（`.summary-count`）略突出（同色系更深/更饱和或加底色胶囊）
- 时间轴布局：
  - `.summary-timeline`：垂直分组列表
  - `.day-group`：每个日期一组，组内 `grid` 排列卡片（类似相册）
  - `.date-stamp`：左上角日期印章（年 / 月 / 日 三行或两行排版）
  - `.event-card`：延续现有圆角、柔和边框、轻阴影
  - `.event-time`：卡片左上角时间戳（HH:mm）
  - `.event-title`：任务名（可 2 行截断，避免卡片高度爆炸）
- 响应式：
  - 宽屏：2–3 列网格
  - 小屏：1–2 列网格

### 4) 渲染：根据历史动态生成总结页内容

修改 [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js)：

- 在 `els` 中补齐总结页元素引用：
  - `summaryCount`、`summaryTimeline`
- 新增渲染函数：
  - `renderSummary()`：
    - `summaryCount.textContent = history.length`
    - 将 `history` 按 `completedAt` 倒序排序
    - 按日期（本地时区的 YYYY-MM-DD）分组
    - 每组渲染：
      - 日期印章：年、月、日
      - 事件卡片网格：每张卡左上角时间（HH:mm），主体为任务名
    - 无历史时显示空态
- 调用时机：
  - `boot()` 后调用一次
  - 每次成功记录完成事件后调用
  - 切换到“总结”视图（`setView('summary')`）时调用一次，保证 UI 最新
- 格式化策略：
  - 使用 `Intl.DateTimeFormat('zh-CN', ...)` 或手写补零，输出：
    - 日期：YYYY 年、MM 月、DD 日
    - 时间：HH:mm（24 小时制）

### 5) PWA 缓存版本更新

修改 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html#L11-L138) 与 [sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js#L1-L3)：

- bump `styles.css`、`app.js` 的 query 版本（例如 `v=18`）
- bump `CACHE_NAME`（例如 `adhd-launcher-v21`），并同步 `ASSETS` 列表的版本号

## Verification

- 造数验证：
  - 在“启动”界面生成清单，逐步勾选直至全部完成（触发礼花/完成提示）
  - 连续完成 2–3 次不同任务
- 总结页展示：
  - 切到“总结”：顶部标题中的 `x` 正确等于完成的大任务次数
  - 下方按日期分组显示卡片；每张卡左上角显示 HH:mm；主体显示任务名
  - 同一天完成多次：同一天分组下出现多张卡，时间不同
  - 没有历史时：显示空态提示
- 兼容性：
  - 老用户只有旧 localStorage 时：不报错，`x=0`，可继续使用并产生新记录
  - `prefers-reduced-motion` 下：不影响可用性（总结页不依赖强动画）

