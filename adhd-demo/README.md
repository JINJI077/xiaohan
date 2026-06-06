# ADHD 事项启动器 Demo

把一个“大任务”拆成可以马上开始的小步骤。项目可以离线使用，也可以通过本地代理调用 DeepSeek/OpenAI 兼容接口启用 AI 拆解。

## 推荐用法：启用 AI

给别人使用时，推荐让对方按下面步骤操作：

1. 安装 Node.js 18 或更新版本：<https://nodejs.org/>
2. 下载并解压整个项目文件夹，不要只拷贝 `index.html`。
3. 双击项目里的 `start.bat`。
4. 浏览器会自动打开 `http://127.0.0.1:5173/`。
5. 展开页面里的 “API 设置（可选 / optional）”，填写：
   - 调用方式：`本地代理（推荐）/ Proxy`
   - API Key：你的 DeepSeek/OpenAI 兼容 Key
   - Base URL：默认 `https://api.deepseek.com`，也可以填其他 OpenAI-compatible 地址
   - Model：默认 `deepseek-chat`

使用 AI 时请保持 `start.bat` 打开的窗口不要关闭；关闭窗口后本地代理会停止。

## 离线用法：不启用 AI

- 可以直接双击 `index.html`。
- 这种方式是 `file://` 页面，只能使用内置的本地规则拆解，不会调用 AI。
- 如果你看到“当前使用本地规则（不是 AI）”，说明 AI 没有成功启用。

## 为什么双击 HTML 不能调用 AI？

浏览器直接打开 `index.html` 时，页面地址是 `file://`。此时默认的 Proxy 请求 `/api/llm/chat` 没有本地服务器接收，所以 AI 请求不会成功。

Direct 直连 API 也不推荐：很多 API 服务会被浏览器 CORS 策略拦截，而且 API Key 会暴露在前端页面里。这个项目推荐用 `start.bat` 启动本地代理，再从 `http://127.0.0.1:5173/` 打开页面。

## 手动启动

如果不想双击脚本，也可以在项目目录中运行：

```bash
node local-proxy.mjs
```

然后打开：

```text
http://127.0.0.1:5173/
```

如果端口被占用，可以换端口：

```bat
set PORT=3000 && start.bat
```

或：

```bat
set PORT=3000 && node local-proxy.mjs
```

## 常见问题

### “生成出来前几步总是一模一样”

通常表示没有成功调用 AI，而是降级用了本地规则。请检查：

- 是否是双击 `index.html` 打开的 `file://` 页面。
- 是否已经双击 `start.bat` 并打开了 `http://127.0.0.1:5173/`。
- `start.bat` 窗口是否还开着。
- API Key、Base URL、Model 是否填写并保存。
- Direct 模式是否被浏览器 CORS 拦截。

### “别人电脑上启动失败”

- 提示未检测到 Node.js：安装 Node.js 18+。
- 提示 Node 版本太低：升级 Node.js。
- 提示端口被占用：关闭占用端口的程序，或运行 `set PORT=3000 && start.bat`。
- 浏览器打开后仍不是 AI：确认打开的是 `http://127.0.0.1:5173/`，不是本地文件 `index.html`。
