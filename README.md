# xiaohan

## adhd-demo（事项启动器 + 可选 AI）

- 纯前端本地拆解：直接双击 [adhd-demo/index.html](adhd-demo/index.html)
- 启用 AI（推荐 Proxy，本地代理转发，避免 CORS）：
  - 安装 Node.js 18+
  - 运行：`node adhd-demo/local-proxy.mjs`
  - 浏览器打开输出的 `http://localhost:5173/`（如 localhost 解析异常，可改用 `http://127.0.0.1:5173/`）
  - 在页面的 API 设置里填入 API Key（Base URL 默认是 DeepSeek/OpenAI 兼容地址，可按需修改）

更多细节见：[adhd-demo/README.md](adhd-demo/README.md)

## pomodoro-demo（番茄钟）

打开 [pomodoro-demo/index.html](pomodoro-demo/index.html) 即可运行（纯静态 HTML/CSS/JS，无需安装依赖）。

快捷键：

- Space：开始/暂停
- R：重置

功能：

- “时长”：可调整专注时长与强制休息时长（默认 25/5 分钟），会自动保存
- 强制休息：专注结束后自动进入强制休息倒计时，期间禁止跳过与切换模式（允许暂停/继续与重置）
