"""README diagrams must stay visible on GitHub mobile."""

from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
README = ROOT / "README.md"

DIAGRAMS = ("klarpost-mark", "architecture", "evaluation", "action-ladder")


def test_diagram_svgs_are_utf8_xml():
    svgs = sorted(ASSETS.glob("*.svg"))
    assert svgs, "expected SVG sources under docs/assets/"
    for svg in svgs:
        text = svg.read_text(encoding="utf-8")
        ET.fromstring(text)


def test_readme_embeds_png_diagrams_not_svg():
    readme = README.read_text(encoding="utf-8")
    for name in DIAGRAMS:
        png = ASSETS / f"{name}.png"
        assert png.is_file(), f"missing {png}"
        assert png.stat().st_size > 0
        assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert f"docs/assets/{name}.png" in readme
        assert f"docs/assets/{name}.svg" not in readme
