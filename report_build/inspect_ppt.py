from __future__ import annotations

import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计")
FILES = ["NILM-pre10.21.pptx", "pre-10.7.pptx", "NILM_4.pptx"]


def theme_info(path: Path) -> None:
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.startswith("ppt/theme/theme") and n.endswith(".xml")]
        if not names:
            return
        xml = z.read(names[0]).decode("utf-8", "ignore")
    import re

    print("  theme file:", names[0])
    for tag in ("a:dk1", "a:lt1", "a:dk2", "a:lt2", "a:accent1", "a:accent2", "a:accent3", "a:accent4", "a:accent5", "a:accent6"):
        m = re.search(rf"<{tag}>.*?val=\"([0-9A-Fa-f]{{6}})\"", xml, re.S)
        if m:
            print(f"    {tag}: #{m.group(1)}")
    for tag in ("a:majorFont", "a:minorFont"):
        block = re.search(rf"<{tag}>.*?</{tag}>", xml, re.S)
        if block:
            m = re.search(r"<a:latin typeface=\"([^\"]*)\"", block.group(0))
            ea = re.search(r"<a:ea typeface=\"([^\"]*)\"", block.group(0))
            print(f"    {tag}: latin={m.group(1) if m else ''} ea={ea.group(1) if ea else ''}")


def color_of(fill):
    try:
        if fill.type is not None and fill.fore_color.rgb is not None:
            return f"#{fill.fore_color.rgb}"
    except Exception:
        pass
    return None


for name in FILES:
    path = ROOT / name
    if not path.exists():
        continue
    prs = Presentation(str(path))
    print("=" * 90)
    print(name, f"slides={len(prs.slides)} size={Emu(prs.slide_width).inches:.2f}x{Emu(prs.slide_height).inches:.2f} in")
    theme_info(path)
    for idx, slide in enumerate(prs.slides, start=1):
        bg = None
        try:
            bg = color_of(slide.background.fill)
        except Exception:
            pass
        texts, pics, charts, tables = [], 0, [], 0
        for shape in slide.shapes:
            if shape.has_text_frame:
                txt = " ".join(p.text.strip() for p in shape.text_frame.paragraphs if p.text.strip())
                if txt:
                    texts.append(txt[:70])
            if shape.shape_type == 13:
                pics += 1
            if getattr(shape, "has_chart", False):
                charts.append(str(shape.chart.chart_type).split(".")[-1])
            if getattr(shape, "has_table", False):
                tables += 1
        print(f"  [{idx:02d}] layout={slide.slide_layout.name!r} bg={bg} shapes={len(slide.shapes)} pics={pics} charts={charts} tables={tables}")
        for t in texts[:6]:
            print("       ·", t)
