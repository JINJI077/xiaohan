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

