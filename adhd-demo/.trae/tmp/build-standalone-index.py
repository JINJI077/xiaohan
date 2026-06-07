from __future__ import annotations

import base64
import re
from pathlib import Path


def to_data_uri_png(path: Path) -> str:
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def replace_js_const(js: str, name: str, value: str) -> str:
    pattern = re.compile(rf'^(const\s+{re.escape(name)}\s*=\s*).+?;\s*$', re.MULTILINE)
    return pattern.sub(lambda m: f'{m.group(1)}"{value}";', js)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    index_path = root / "index.html"
    css_path = root / "styles.css"
    js_path = root / "app.js"

    garden_uri = to_data_uri_png(root / "图片素材" / "花园.png")
    grass_sprout_uri = to_data_uri_png(root / "图片素材" / "小草-没花.png")
    grass_bloom_uri = to_data_uri_png(root / "图片素材" / "小草-有花版本.png")

    html = index_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    js = js_path.read_text(encoding="utf-8")

    js = replace_js_const(js, "GRASS_SPROUT_SRC", grass_sprout_uri)
    js = replace_js_const(js, "GRASS_BLOOM_SRC", grass_bloom_uri)

    html = re.sub(
        r'<link\s+rel="stylesheet"\s+href="[^"]*"\s*/?>',
        lambda _: f"<style>\n{css}\n</style>",
        html,
        count=1,
    )

    html = re.sub(
        r'<script\s+src="[^"]*app\.js[^"]*"\s+defer></script>',
        lambda _: f"<script>\n{js}\n</script>",
        html,
        count=1,
    )

    html = html.replace('src="./图片素材/花园.png"', f'src="{garden_uri}"')

    index_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()

