$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$port = if ($env:PORT) { $env:PORT } else { "5173" }
$url = "http://127.0.0.1:$port/"

Write-Host ""
Write-Host "ADHD 事项启动器 - 本地 AI 代理启动器"
Write-Host "====================================="
Write-Host ""

$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
  Write-Host "未检测到 Node.js。请先安装 Node.js 18 或更新版本：https://nodejs.org/"
  Read-Host "Press Enter to exit"
  exit 1
}

$major = node -p "process.versions.node.split('.')[0]"
if ([int]$major -lt 18) {
  Write-Host "当前 Node.js 主版本是 $major，本项目需要 Node.js 18 或更新版本。"
  Read-Host "Press Enter to exit"
  exit 1
}

Write-Host "Node.js 检查通过。"
Write-Host "即将打开：$url"
Write-Host "请不要关闭这个窗口；关闭后 AI 代理也会停止。"
Write-Host ""

Start-Process $url
node .\local-proxy.mjs

Write-Host ""
Write-Host "本地代理已停止。如果端口被占用，可以设置 PORT 环境变量后重试。"
Read-Host "Press Enter to exit"
