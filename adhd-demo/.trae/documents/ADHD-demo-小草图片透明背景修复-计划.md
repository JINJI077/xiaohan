# ADHD-demo-小草图片透明背景修复-计划

## Summary
把右下角“小草进度”用到的两张小草图片（`图片素材/小草-没花.png`、`图片素材/小草-有花版本.png`）从“自带棋盘格底图”处理为“真正透明背景”，保证页面上不再出现白色方格/棋盘格底。

## Current State Analysis
- 右下角小草组件在 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html) 中通过 `<img id="grassProgressImg">` 渲染。
- 小草图片路径由 [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js#L3-L5) 的常量 `GRASS_SPROUT_SRC / GRASS_BLOOM_SRC` 指向两张 PNG。
- 当前仓库中没有对应 SVG，仅有：
  - `图片素材/小草-没花.png`
  - `图片素材/小草-有花版本.png`
- 这两张 PNG 的“透明区域”被直接烘焙成了棋盘格像素（浏览器不会自己显示棋盘格），导致在页面右下角看到明显方格底。
- PWA 缓存由 [sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js) 控制，`CACHE_NAME` 目前为 `adhd-launcher-v27`，并预缓存上述两张 PNG。

## Proposed Changes

### 1) 离线处理 PNG：把棋盘格像素抠成透明
目标文件：
- `图片素材/小草-没花.png`
- `图片素材/小草-有花版本.png`

处理方式（一次性脚本，生成后的 PNG 直接提交到仓库，运行时不依赖任何库）：
- 在本机用 Python + Pillow 读取 PNG，输出带 alpha 的 PNG（覆盖原文件或输出为同名文件）。
- 自动推断棋盘格背景色：
  - 采样图片四周边缘（如 10px 宽的边框）统计出现频率最高的 2~3 个颜色，视为背景色候选（通常是白色/浅灰）。
- 对每个像素计算与背景色候选的最小 RGB 距离（欧氏距离）：
  - 距离小于阈值 `t0` → alpha=0（完全透明）
  - 距离大于阈值 `t1` → alpha=255（完全不透明）
  - 介于 `t0..t1` 之间 → 按比例渐变（避免边缘出现锯齿/硬边）
- 仅修改 alpha，不改变原 RGB（最大程度保留水彩风格与花朵颜色）。

说明：
- 这是“抠透明背景”的实质做法，能保留浅色花朵（比“按亮度阈值一刀切”更稳）。
- 如果第一次阈值不理想（误抠花瓣/残留棋盘格），只需微调 `t0/t1` 重新运行脚本即可。

### 2) 缓存版本递增，确保用户端立刻生效
文件： [sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js)
- 将 `CACHE_NAME` 从 `adhd-launcher-v27` 递增到 `adhd-launcher-v28`（或更高）。
- `ASSETS` 中仍保留两张 PNG 路径不变（因为文件内容已更新），但通过新 cache name 强制重新 precache。

（可选但推荐）同时递增 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html) 的 `styles.css/app.js` 查询参数版本号，进一步避免用户端“只更新了 SW，但页面资源仍被浏览器缓存命中”的偶发现象。

### 3) 不改业务逻辑
文件： [app.js](file:///d:/Github_Try/xiaohan/adhd-demo/app.js)
- 不需要改动 `GRASS_*_SRC` 路径（仍指向同名 PNG），只替换图片文件内容即可。

## Assumptions & Decisions
- 以你的最新选择为准：优先“把现有两张小草图片抠成真正透明背景”，不强制改成 SVG。
- 图片处理为一次性离线步骤；仓库最终提交的是已处理好的 PNG 文件，线上运行不引入新依赖。

## Verification
- 本地打开启动页，生成清单后右下角小草出现，图片四周与草叶间隙不再显示棋盘格/白色方格。
- 进度达到 90% 后切换到开花版本，花朵颜色不被误抠除、边缘无明显白边/硬边。
- 刷新页面后仍然正常（验证 `CACHE_NAME` 递增触发 SW 更新，离线缓存也能加载到新图片）。

