# ADHD-demo-总结页花园抠图并居中展示-计划

## Summary
把 `图片素材/花园.png` 的“棋盘格底图”抠成真正透明背景，并把处理后的图片放到“总结”页面内容顶部居中展示。

## Current State Analysis
- “总结”页面在 [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html#L118-L131) 的 `#viewSummary` 中渲染，目前顶部只有 `.summary-hero` 标题区，没有装饰图。
- 目标图片已存在：`图片素材/花园.png`，但图片里的棋盘格是被烘焙进像素的底图（不是浏览器自动显示的透明背景提示）。
- PWA 预缓存由 [sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js#L1-L11) 的 `ASSETS` 控制，目前未包含 `图片素材/花园.png`。

## Proposed Changes

### 1) 离线处理 PNG：把棋盘格像素抠成透明
目标文件：
- `图片素材/花园.png`

处理方式（一次性离线步骤，产物直接提交到仓库，运行时不依赖任何库）：
- 使用 Python + Pillow 读取 PNG，通过“从四周边界泛洪填充”只抠掉与边界连通的背景区域（避免误抠画面内部的白色花瓣）。
- 背景候选色自动推断：采样图片四周边缘（10px 宽边框）统计出现频率最高的 2 个颜色作为背景候选。
- 背景判定（RGB 距离 + 亮度门槛）：
  - 计算像素与背景候选色的最小 RGB 欧氏距离 `d`（0~441）。
  - 像素亮度门槛：`min(r,g,b) >= 235`（避免把米黄色小路、淡色墙体误当背景）。
  - 两个阈值（固定值，后续只在验收失败时再调）：
    - `d_strict = 12`（用于从边界开始的种子点）
    - `d_loose = 40`（用于泛洪扩展与边缘柔化）
- alpha 生成：
  - 若像素在“与边界连通的背景 mask”中：alpha=0
  - 若像素不在 mask 中，但与 mask 相邻（4 邻域）且 `d < d_loose`：alpha 按 `d_strict..d_loose` 线性插值到 `0..255`（柔化边缘）
  - 其他像素：alpha=255

执行脚本（作为临时文件生成，运行完即可删除，不长期保留在仓库）：
- 依赖安装（如未安装）：`python -m pip install pillow`
- 新建临时脚本：`.trae/tmp/make_transparent_png.py`，内容如下（固定处理输入路径并原地覆盖）：

```python
from __future__ import annotations

import math
from collections import Counter, deque
from pathlib import Path

from PIL import Image


def rgb_dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def main() -> None:
    src = Path("图片素材/花园.png")
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    px = img.load()

    border = 10
    colors: list[tuple[int, int, int]] = []
    for y in range(h):
        for x in range(w):
            if x < border or x >= w - border or y < border or y >= h - border:
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                colors.append((r, g, b))
    top = [c for c, _ in Counter(colors).most_common(2)]
    if len(top) < 1:
        raise RuntimeError("无法从边缘推断背景色")

    d_strict = 12.0
    d_loose = 40.0
    bright_min = 235

    def dist_to_bg(x: int, y: int) -> float:
        r, g, b, _ = px[x, y]
        return min(rgb_dist((r, g, b), bg) for bg in top)

    def is_bg(x: int, y: int, d_limit: float) -> bool:
        r, g, b, a = px[x, y]
        if a == 0:
            return True
        if min(r, g, b) < bright_min:
            return False
        return dist_to_bg(x, y) <= d_limit

    mask = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    def try_push(x: int, y: int) -> None:
        if mask[y][x]:
            return
        if not is_bg(x, y, d_strict):
            return
        mask[y][x] = True
        q.append((x, y))

    for x in range(w):
        try_push(x, 0)
        try_push(x, h - 1)
    for y in range(h):
        try_push(0, y)
        try_push(w - 1, y)

    while q:
        x, y = q.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if mask[ny][nx]:
                continue
            if not is_bg(nx, ny, d_loose):
                continue
            mask[ny][nx] = True
            q.append((nx, ny))

    def has_bg_neighbor(x: int, y: int) -> bool:
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if mask[ny][nx]:
                return True
        return False

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if mask[y][x]:
                px[x, y] = (r, g, b, 0)
                continue
            if not has_bg_neighbor(x, y):
                continue
            d = dist_to_bg(x, y)
            if d >= d_loose:
                continue
            t = (d - d_strict) / max(d_loose - d_strict, 1e-6)
            alpha = int(max(0.0, min(1.0, t)) * 255)
            px[x, y] = (r, g, b, alpha)

    img.save(src, "PNG")


if __name__ == "__main__":
    main()
```

产出策略：
- 直接覆盖 `图片素材/花园.png`（路径不变，页面引用更简单）。

### 2) 在“总结”页顶部居中插入图片
文件： [index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html#L118-L131)
- 在 `#viewSummary` 内、`.summary-hero` 之前插入一个装饰图容器，例如：
  - `<div class="summary-top-art" aria-hidden="true"><img class="summary-top-art-img" src="./图片素材/花园.png" alt="" /></div>`
- 图片作为装饰用途：`alt=""` 且容器 `aria-hidden="true"`，避免影响可访问性朗读。

### 3) 添加对应样式，保证“上面中间”并自适应
文件： [styles.css](file:///d:/Github_Try/xiaohan/adhd-demo/styles.css)
- 新增样式（固定值，直接按下列写入）：
  - `.summary-top-art`：
    - `display:flex; justify-content:center;`
    - `padding: 8px 0 6px;`
  - `.summary-top-art-img`：
    - `display:block;`
    - `width: min(640px, 100%);`
    - `height: auto;`
    - `user-select: none;`

### 4) 更新 PWA 预缓存与资源版本，确保用户端立刻生效
文件： [sw.js](file:///d:/Github_Try/xiaohan/adhd-demo/sw.js#L1-L11)、[index.html](file:///d:/Github_Try/xiaohan/adhd-demo/index.html#L11-L12)
- `sw.js`
  - `CACHE_NAME` 从 `adhd-launcher-v31` 递增到 `adhd-launcher-v32`，强制用户端重新 precache。
  - `ASSETS` 增加 `./图片素材/花园.png`。
  - 同步把 `ASSETS` 里的 `./styles.css?v=28`、`./app.js?v=28` 递增为 `v=29`（因为本次会改 `index.html/styles.css`），避免浏览器 HTTP 缓存偶现命中旧内容。
- `index.html`
  - 把 `./styles.css?v=28`、`./app.js?v=28` 递增为 `v=29`，与 SW 的 `ASSETS` 保持一致。

## Assumptions & Decisions
- 目标是“真正透明背景”，不通过 CSS 伪装遮挡棋盘格。
- 图片放在“总结”卡片内容区内的最上方，居中展示；不做背景图铺满（避免干扰正文可读性）。
- 图片处理为离线一次性步骤；最终仓库里提交的是已经带 alpha 的 PNG。

## Verification
- 本地启动（`start.bat` 或 `node local-proxy.mjs`）打开 `http://127.0.0.1:5173/`，切换到“总结”：
  - 顶部出现花园图，水平居中。
  - 图片周围不再出现棋盘格/白色方块底色，页面背景能透出来。
- 刷新页面并等待 SW 更新后再次打开：
  - 离线刷新仍能加载到花园图（验证 `ASSETS` + `CACHE_NAME` 生效）。
