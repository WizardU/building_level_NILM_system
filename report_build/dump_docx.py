from __future__ import annotations

import sys
from pathlib import Path

from docx import Document

path = Path(sys.argv[1])
doc = Document(path)
print(f"FILE: {path.name}")
print(f"paragraphs={len(doc.paragraphs)} tables={len(doc.tables)} sections={len(doc.sections)}")
print("=" * 100)
for index, paragraph in enumerate(doc.paragraphs):
    text = paragraph.text.strip()
    if not text:
        continue
    style = paragraph.style.name if paragraph.style is not None else ""
    print(f"[P{index:03d}][{style}] {text}")
print("=" * 100)
for t_index, table in enumerate(doc.tables):
    print(f"\n[TABLE {t_index + 1}] rows={len(table.rows)} cols={len(table.columns)}")
    for row_index, row in enumerate(table.rows):
        cells = []
        for cell in row.cells:
            cells.append(" ".join(cell.text.split()))
        print(f"  R{row_index:02d}: " + " | ".join(cells))
