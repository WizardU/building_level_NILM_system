from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation

path = Path(sys.argv[1])
prs = Presentation(path)
print(f"FILE: {path.name}")
print(f"slides={len(prs.slides)} size={prs.slide_width}x{prs.slide_height}")
print("=" * 100)
for s_index, slide in enumerate(prs.slides, 1):
    print(f"\n--- SLIDE {s_index} ---")
    for shape in slide.shapes:
        if shape.has_text_frame:
            text = shape.text_frame.text.strip()
            if text:
                print(text)
        if getattr(shape, "has_table", False) and shape.has_table:
            print("[TABLE]")
            for row in shape.table.rows:
                print(" | ".join(" ".join(c.text.split()) for c in row.cells))
        if shape.has_chart:
            print("[CHART]", shape.chart.chart_type)
    if slide.has_notes_slide:
        note = slide.notes_slide.notes_text_frame.text.strip()
        if note:
            print("[NOTES]", note)
