# ADHD 事项启动器 Demo

## 直接使用（不启用 AI）

- 双击打开 `index.html`
- 不需要安装任何依赖

注意：这种打开方式是 `file://`，只能使用“本地规则拆解”（不是 AI 输出）。

## 启用 AI（推荐：Proxy 本地代理）

### 1) 安装 Node.js

- 建议 Node.js 18+（本项目代理使用全局 fetch）

### 2) 启动本地服务

在仓库根目录执行：

```bash
node adhd-demo/local-proxy.mjs
```

或 Windows 直接双击：

- `adhd-demo/start.bat`

启动成功会输出类似：

- `http://127.0.0.1:5173/`

用浏览器打开这个地址（不要再双击 index.html）。

### 3) 在页面里填 API Key

展开 “API 设置（可选 / optional）”：

- 调用方式：选择 “本地代理（推荐）/ Proxy”
- API Key：填入你的 Key（只保存在你的浏览器本地）
- Base URL：默认是 `https://api.deepseek.com`（也可填 OpenAI 兼容地址）
- Model：默认 `deepseek-chat`

## 常见问题

### “AI 生成功能前几步都一模一样”

通常表示并没有成功调用 AI，而是降级使用了本地规则拆解：

- Proxy 模式但你是双击 index.html（file://）打开
- Proxy 模式但本地服务没启动
- Direct 模式被浏览器 CORS 拦截
- Key/URL 配置不完整

### “别人电脑上启动服务失败”

- 报 `fetch is not defined` / 类似错误：升级到 Node.js 18+
- 端口被占用：设置 `PORT` 环境变量换端口（例如 Windows：`set PORT=3000` 后再启动）

