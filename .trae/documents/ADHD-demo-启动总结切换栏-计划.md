## Summary

为 ADHD Demo 新增“启动 / 总结”两界面切换：在屏幕最上方居中放置两枚白字按钮；当前界面用更深、更澄澈的湛蓝色块高亮；hover 到另一枚按钮时也出现同样蓝色块（双高亮）；点击切换时由较深色块以非线性（慢启快动慢停）方式移动到另一词，并显示对应界面（先做“总结”占位，后续再深化）。

## Current State Analysis

- 页面结构是单页静态 HTML + 原生 JS 操作 DOM，无路由框架：[index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html)
- JS 事件分发通过 `data-action` 统一处理：[wire](file:///d:/Github_Try/xiaohan/adhd-demo/app.js#L44-L113)
- UI 更新采用 `render()` 重绘列表区域，不影响页面整体骨架：[app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js#L611-L633)
- 现有动画体系以 CSS transition/keyframes 为主，并在 `prefers-reduced-motion` 下禁用部分动效：[styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css#L836-L855)
- Service Worker 预缓存了 `index.html / styles.css?v=16 / app.js?v=16`，变更后需要同步 bump 版本与缓存名避免旧资源被命中：[sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js#L1-L3)

## Assumptions & Decisions

- “启动 / 总结”采用“两张 card 切换显示”的方式，不破坏现有启动页 DOM 与渲染逻辑。（用户已确认）
- Hover 行为为“双高亮”：保持当前选中项的蓝色块，同时 hover 的另一项也出现同样的蓝色块。（用户已确认）
- 点击切换时的移动曲线使用慢启快动慢停（ease-in-out 风格）。（用户已确认）
- “总结”页当前仅做结构与占位文案，不新增数据模型与持久化；后续深化时再补充“已完成的大任务”统计/列表。

## Proposed Changes

### 1) 新增顶部居中切换栏（HTML）

修改 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html)：

- 在 `<body>` 内、`.app` 之前插入一个固定定位的导航容器（例如 `nav.view-switch`）：
  - 两个按钮：`启动`、`总结`（白色字体）
  - 一个绝对定位的“深蓝色块指示器”元素（作为点击切换时移动的主体）
  - 给按钮增加 `data-action="view-start"` / `data-action="view-summary"`，复用现有的 `data-action` 分发模式
- 给现有 `<main class="card">` 增加 id/class（例如 `id="viewStart"`），作为“启动页 card”
- 新增第二张 `<main class="card">` 作为“总结页 card”（例如 `id="viewSummary"`），内部先放：
  - 标题“总结”
  - 一行占位描述（例如：这里会汇总你做完的“大任务”）
- 初始状态：显示启动页 card，隐藏总结页 card（建议使用 `hidden` 属性，便于无障碍与减少 CSS 复杂度）

### 2) 顶部切换栏样式与动效（CSS）

修改 [styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css)：

- 新增颜色变量（或直接在组件内定义）：
  - 更深、更澄澈的湛蓝色（用于色块填充）
  - 白色字体与轻微阴影/描边，确保在浅背景上可读
- `.view-switch` 固定在屏幕顶部居中：
  - `position: fixed; left: 50%; transform: translateX(-50%); top: calc(14px + env(safe-area-inset-top));`
  - 适当的 `z-index`，高于 card
  - 允许背景微透明 + blur（可选），让白字更稳定
- 指示器 `.view-switch-indicator`：
  - `position: absolute; inset-block: 0;`（或用 top/bottom）
  - `border-radius` 做成“圆角色块”
  - `transition: transform ... cubic-bezier(...), width ... cubic-bezier(...)` 实现慢启快动慢停
- Hover 双高亮：
  - 对按钮 `.view-switch-tab` 做 `::before`（或额外 span）作为 hover 色块，默认 `opacity: 0`
  - hover/focus 时 `opacity: 1`（保持指示器仍在当前选中项上）
- 适配降动效：
  - 在 `@media (prefers-reduced-motion: reduce)` 下，为 `.view-switch-indicator`/hover 动效设置 `transition: none`
- 让主内容不被顶部固定栏遮挡：
  - 增加 `.app` 的 `padding-top`（或在 nav 下留出空间），保证小屏下顶部不会压住卡片

### 3) 切换逻辑与指示器定位（JS）

修改 [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js)：

- 扩展 `els`：
  - `viewStart` / `viewSummary`
  - `viewSwitch` / `viewIndicator`
  - 两个 tab 按钮（可 querySelectorAll）
- 新增 `ui` 层状态（不影响原 `state` 数据结构）：
  - `let currentView = "start"`（可选：放入 localStorage，与 `state` 同步保存）
- 在 `wire()` 的 `data-action` 分发中新增：
  - `view-start` → 切换到启动页
  - `view-summary` → 切换到总结页
- 视图切换实现：
  - 设置 `viewStart.hidden = currentView !== "start"`
  - 设置 `viewSummary.hidden = currentView !== "summary"`
  - 同步更新 tab 的 aria 状态（例如 `aria-current="page"` 或 `aria-selected`）
- 指示器定位实现：
  - 在初始化、切换、窗口 resize 时，根据目标 tab 的 `getBoundingClientRect()` 计算：
    - 相对 `.view-switch` 容器的 x 偏移
    - tab 宽度
  - 更新指示器的 `transform: translateX(...)` 与 `width: ...px`
  - 点击切换时依赖 CSS transition 完成“非线性移动”
- Hover 双高亮实现：
  - 对 tab 监听 `pointerenter/pointerleave` 或 `mouseenter/mouseleave`：
    - hover 时给对应 tab 加 `is-hover`（触发 `::before` 色块）
    - 不改变 currentView，不移动指示器
  - 同步处理 `focus/blur`（键盘可用）

### 4) 更新离线缓存版本（PWA）

修改 [sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js) 与 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html#L11-L116)：

- bump `styles.css` 与 `app.js` 的 query 版本号（例如 `v=17`）
- bump `CACHE_NAME`（例如 `adhd-launcher-v20`），确保 Service Worker 安装时会拉取新资源
- 同步更新 `ASSETS` 内的 `styles.css?v=...`、`app.js?v=...`

## Verification

- 本地打开 `adhd-demo/index.html`（file://）：
  - 顶部居中出现“启动 / 总结”白字切换栏
  - 当前为“启动”，深蓝色块在“启动”下方/背后
  - hover 到“总结”时，“总结”也出现同样深蓝底色（双高亮），但不切换页面
  - 点击“总结”后：深蓝色块以慢启快动慢停移动到“总结”，页面切换到“总结”卡片占位
  - 再点击“启动”：同理切回
- 通过 `start.bat` 以 http://127.0.0.1:5173/ 打开：
  - hard refresh 后资源更新生效（Service Worker 不再命中旧缓存）
  - 多次切换不报错（控制台无异常）
- 开启系统“减少动态效果”：
  - 切换仍可用，但不应出现明显过渡动画（符合 `prefers-reduced-motion`）

