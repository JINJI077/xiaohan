## Summary

本计划用于排查并修复两个问题：

- adhd-demo 在你本机“无法调用 AI / 看起来没有根据 AI 输出变化”
- 别人电脑上拉取代码后“打不开 / AI 不工作 / 启动服务失败”

目标是让项目在“无需猜测”的前提下可运行：用户能清楚知道当前是否真的走了 AI、如何启动本地代理、以及在别的电脑上最少需要装什么。

## Current State Analysis

### 代码结构与调用链

- 页面入口：`adhd-demo/index.html`
- 主逻辑：`adhd-demo/app.js`
- 本地代理 + 静态文件服务器：`adhd-demo/local-proxy.mjs`
- AI 请求端点（前端固定写死相对路径）：`const LLM_ENDPOINT = "/api/llm/chat";`（`adhd-demo/app.js`）
- AI 实际触发条件：只有同时配置了 `apiKey` 和 `baseUrl` 才会走 AI；否则直接走本地规则拆解（`shouldUseAi()` + `onGenerate()`）

### 你当前复现方式对应的必然结果

你是“直接双击 `index.html`（file://）打开”。在该模式下：

- 默认 API Mode 是 `proxy`，前端会请求 `"/api/llm/chat"`。
- 由于页面不是通过 `http://127.0.0.1:5173/` 这种同源 HTTP 服务打开，本机并不存在同源的 `/api/llm/chat` 来承接请求，因此 AI 请求会失败。
- 失败后代码会自动降级到 `generateWithLocal()`（toast 提示很短且可能被忽略），所以你会看到“前几步都一模一样”的本地兜底步骤（例如“停 3 秒，深呼吸一下 / 把需要用的东西放到手边 …”），看起来像“提示词错了/没根据输入变化”，实际是“根本没走 AI”。

### 别人电脑“打不开/启动失败”的高概率原因（由代码推断）

- 他们没有安装 Node，或 Node 版本过低（`local-proxy.mjs` 使用全局 `fetch`，Node < 18 通常没有）
- 端口 5173 被占用（默认 `PORT=5173`）
- 他们也用 file:// 打开导致 AI 必然不可用；或尝试 direct 直连被 CORS 拦截
- 根目录 `README.md` 目前只描述了 pomodoro-demo，且链接里使用了带盘符的 file:// 路径（对别人电脑不可用），会造成“按 README 操作打不开”的误解

## Proposed Changes

### 1) 让“是否真的走 AI”对用户更透明（前端提示与失败原因可见）

修改文件：

- `adhd-demo/app.js`

具体改动：

- 在 `onGenerate()` 的 AI 分支里，区分以下失败场景并给出明确 toast：
  - 当前是 `proxy` 模式但页面是 `file://` 打开的：直接提示“需要启动本地代理并用 http://127.0.0.1:5173 打开”
  - fetch 返回非 2xx：显示 `HTTP <status>` + 尝试提取服务端返回的 `error.message`
  - 网络失败/CORS：提示“请求被浏览器拦截（CORS）或代理未启动”
- 失败降级到本地拆解时，在 bubble/toast 里明确标注“当前使用本地规则（不是 AI 输出）”，避免误判为“提示词没效果”

### 2) 降低配置门槛：默认填充 DeepSeek 兼容 Base URL（至少让用户只填 Key 也能尝试）

修改文件：

- `adhd-demo/app.js`
- `adhd-demo/index.html`

具体改动：

- `defaultSettings()` 中将 `baseUrl` 默认值设为 `https://api.deepseek.com`（仍允许用户在 UI 里覆盖）
- `index.html` 里给 Base URL 输入框加 `placeholder="https://api.deepseek.com"`（仅提示，不存储敏感信息）

### 3) 让别人电脑“最小步骤可跑起来”：补齐文档 + 一键启动入口

修改/新增文件：

- `README.md`（根目录）
- 新增 `adhd-demo/README.md`
- 新增 `adhd-demo/start.bat`（Windows 双击启动）
- 可选新增 `adhd-demo/start.ps1`（PowerShell 启动，若执行策略允许）

文档要点：

- 明确 adhd-demo 的正确启动方式：
  - 安装 Node（建议 Node 18+）
  - 运行 `node adhd-demo/local-proxy.mjs`
  - 浏览器打开输出的 `http://127.0.0.1:5173/`
- 解释两种模式：
  - Proxy（推荐）：避免 CORS，但需要 Node
  - Direct：可能被 CORS 拦截，不推荐
- 常见错误自查：
  - “页面能开但 AI 不工作”= 没填 baseUrl/key / 没启动代理 / CORS
  - “启动服务报 fetch not defined”= Node 版本过低
  - “端口占用”= 设置 `PORT=...`

根目录 README 修正：

- 把当前 pomodoro-demo 的 file:// 绝对路径改为相对路径链接，确保别人电脑点开也正确
- 增加 adhd-demo 的启动说明入口（指向 `adhd-demo/README.md`）

### 4) 代理端启动失败更友好（Node 版本与 fetch 可用性检查）

修改文件：

- `adhd-demo/local-proxy.mjs`

具体改动：

- 启动时检测 `globalThis.fetch` 是否存在；不存在则输出清晰提示并退出（例如“请升级到 Node 18+”）
- 启动日志输出更明确：当前端口、可用的访问 URL、如何修改端口（`PORT`）

## Assumptions & Decisions

- 以“Proxy 本地代理”为默认可用路径（最稳、规避 CORS），并把“直接双击 index.html”的体验调整为：页面能用本地拆解，但一旦配置了 AI，就会提示必须用代理方式打开
- 不在仓库中写入任何真实 API Key；仍只允许用户在本地浏览器或环境变量里配置
- 你希望“只要能用即可”，因此优先保证“可跑 + 可定位问题”，而不是引入复杂框架/依赖

## Verification Steps

- 本机验证（无 Key）：
  - 双击 `adhd-demo/index.html`：应能生成本地拆解，并在 UI 明确显示“当前使用本地规则”
- 本机验证（有 Key，Proxy 模式）：
  - 运行 `node adhd-demo/local-proxy.mjs`，打开 `http://127.0.0.1:5173/`
  - 在设置里填入 API Key（Base URL 默认已有/或填入）
  - 点击“生成清单”：应看到“AI done”提示；控制台网络请求应命中 `/api/llm/chat`
- 失败可解释性验证：
  - 关闭代理后在 Proxy 模式点击生成：toast 应提示“代理未启动/需要 http 打开”
  - Direct 模式下若被 CORS 拦：toast 应提示 CORS/浏览器拦截
- 迁移验证（别人电脑）：
  - 按 `adhd-demo/README.md` 步骤操作，能成功启动并打开页面（至少本地拆解可用；有 Key 时 AI 可用）

