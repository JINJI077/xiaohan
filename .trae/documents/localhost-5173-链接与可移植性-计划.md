## Summary

将项目中所有对外展示的访问地址从 `http://127.0.0.1:5173/` 统一改为 `http://localhost:5173/`，并确保在不同电脑/不同 IPv4/IPv6 环境下用 `localhost` 打开也稳定可用。

## Current State Analysis

### 目前写死/展示 127.0.0.1 的位置

- 本地代理监听与启动输出：
  - `adhd-demo/local-proxy.mjs` 使用 `server.listen(port, "127.0.0.1", ...)` 且输出 `http://127.0.0.1:${port}/`
    - 见 [local-proxy.mjs](file:///d:/Github_Try/xiaohan/adhd-demo/local-proxy.mjs#L80-L84)
- 前端提示文案（Proxy + file:// 降级提示）：
  - `adhd-demo/app.js` 文案中包含 `http://127.0.0.1:5173/`
    - 见 [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js#L114-L145) 与 [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js#L244-L256)
- 文档：
  - 根 `README.md` 与 `adhd-demo/README.md` 仍展示 `http://127.0.0.1:5173/`
    - 见 [README.md](file:///d:/Github_Try/xiaohan/README.md#L3-L12)、[adhd-demo/README.md](file:///d:/Github_Try/xiaohan/adhd-demo/README.md#L16-L33)

### 为什么仅改“显示成 localhost”还不够

部分系统/浏览器对 `localhost` 会优先解析到 IPv6 的 `::1`。如果服务只监听在 `127.0.0.1`（IPv4），则访问 `http://localhost:5173/` 可能失败。因此需要让代理监听同时兼容 IPv4 与 IPv6 的 localhost 访问。

## Proposed Changes

### 1) local-proxy 监听策略改为兼容 localhost（IPv4+IPv6）

修改文件：

- `adhd-demo/local-proxy.mjs`

改动要点：

- 将 `server.listen(port, "127.0.0.1", ...)` 改为不指定 host（或指定为同时覆盖 IPv4/IPv6 的方式），以兼容：
  - `http://localhost:${port}/`（可能解析到 `::1` 或 `127.0.0.1`）
  - `http://127.0.0.1:${port}/`（仍可用，避免旧习惯断掉）
- 将启动输出与 Proxy API 输出统一改为 `http://localhost:${port}/` 形式，减少用户复制粘贴时的困惑。

### 2) 前端提示文案统一改为 localhost

修改文件：

- `adhd-demo/app.js`

改动要点：

- 将 Proxy 相关的提示文案中的 `http://127.0.0.1:5173/` 改为 `http://localhost:5173/`。

### 3) 文档统一改为 localhost，并补充“localhost/127 都能用”的说明

修改文件：

- `README.md`
- `adhd-demo/README.md`

改动要点：

- 文档中所有 `http://127.0.0.1:5173/` 改为 `http://localhost:5173/`
- 增加一句备注：如遇 `localhost` 解析问题，也可尝试 `127.0.0.1`（作为兜底）

## Assumptions & Decisions

- 你的目标是“别人电脑上克隆后按步骤就能跑”，不是“同一台电脑启动后让局域网其它电脑访问”。因此优先确保 `localhost` 访问稳定；是否开放局域网访问不作为本次目标。

## Verification Steps

- 启动本地代理：`node adhd-demo/local-proxy.mjs`
- 检查启动输出显示为 `http://localhost:<port>/`
- 在浏览器分别访问并确认页面正常加载：
  - `http://localhost:5173/`
  - `http://127.0.0.1:5173/`
- 在 `file://`（双击 index.html）场景触发 AI 时，toast 提示中的地址为 `http://localhost:5173/`

