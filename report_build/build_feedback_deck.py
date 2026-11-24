"""Feedback-response deck: what the review asked, what changed, what is next."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

import build_deck as bd

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计")
FIGS = ROOT / "NILM" / "report_build" / "figs"
SHOTS = ROOT / "NILM" / "report_build" / "shots"
OUT = ROOT / "NILM_Review_Response_11.25.pptx"

TEAL = bd.TEAL
TEAL_DARK = bd.TEAL_DARK
LIGHT = bd.LIGHT
BORDER = bd.BORDER
NAVY = bd.NAVY
BODY = bd.BODY
MUTED = bd.MUTED
WHITE = bd.WHITE
GREEN = bd.GREEN
AMBER = bd.AMBER
RED = bd.RED
PALE_GREEN = bd.PALE_GREEN
PALE_RED = bd.PALE_RED


def add_table(slide, rows, x, y, w, h, widths, font_size=9, status_col=2):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(h))
    table = shape.table
    for idx, width in enumerate(widths):
        table.columns[idx].width = Inches(width)
    row_h = h / len(rows)
    for r_idx, row in enumerate(rows):
        table.rows[r_idx].height = Inches(row_h)
        for c_idx, value in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = ""
            cell.margin_left = Inches(0.05)
            cell.margin_right = Inches(0.04)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c_idx != status_col else PP_ALIGN.CENTER
            run = p.add_run()
            run.text = str(value)
            run.font.name = bd.FONT
            run.font.size = Pt(font_size)
            run.font.bold = r_idx == 0
            run.font.color.rgb = WHITE if r_idx == 0 else NAVY
            cell.fill.solid()
            if r_idx == 0:
                cell.fill.fore_color.rgb = TEAL_DARK
            elif status_col is not None and c_idx == status_col:
                if str(value).startswith("Closed"):
                    cell.fill.fore_color.rgb = PALE_GREEN
                elif str(value).startswith("Partial"):
                    cell.fill.fore_color.rgb = RGBColor(0xFF, 0xF3, 0xD6)
                else:
                    cell.fill.fore_color.rgb = PALE_RED
            else:
                cell.fill.fore_color.rgb = WHITE if r_idx % 2 else RGBColor(0xF7, 0xFB, 0xFC)
    return table


def stat_row(slide, items, y=6.20, h=0.65):
    for index, (number, label) in enumerate(items):
        bd.add_stat(slide, number, label, 4.55 + index * 2.70, y, 2.55, h, number_size=18)


def build() -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    prs.core_properties.title = "Review Response - NILM Midterm"
    prs.core_properties.author = "JinXinyi, YangYifei, YuShengbin"

    # 1 — title
    slide = bd.blank(prs)
    bd.add_rect(slide, 0, 0.72, 8.45, 6.05, TEAL, radius=0, shape=bd.MSO_SHAPE.RECTANGLE)
    bd.add_rect(slide, 8.95, 0.72, 3.85, 6.05, bd.GREY_BG, radius=0, shape=bd.MSO_SHAPE.RECTANGLE)
    bd.add_text(slide, "REVIEW RESPONSE  ·  25 NOV 2026", 0.78, 1.18, 6.8, 0.3, 10, WHITE, True, spacing=120)
    bd.add_text(slide, "What we changed\nafter the review", 0.78, 1.72, 7.2, 1.9, 36, WHITE, True, line_spacing=0.94)
    bd.add_text(slide, "8 comments  ·  4 closed  ·  4 partially closed", 0.80, 3.90, 7.0, 0.35, 16, WHITE)
    bd.add_text(
        slide,
        "Only the review comments, the new evidence, and what happens next.",
        0.80,
        4.48,
        7.0,
        0.35,
        11,
        WHITE,
    )
    bd.add_text(slide, "Tag: midterm-2026-11-30-evidence  ·  21/21 API checks", 0.80, 5.95, 7.0, 0.30, 10, WHITE)
    bd.add_text(slide, "8", 9.20, 2.20, 1.4, 0.9, 58, TEAL_DARK, True)
    bd.add_text(slide, "comments", 9.25, 3.05, 3.2, 0.28, 10, BODY)
    bd.add_text(slide, "4", 9.20, 3.75, 1.2, 0.7, 42, GREEN, True)
    bd.add_text(slide, "closed", 9.80, 4.00, 2.4, 0.28, 10, BODY)
    bd.add_text(slide, "4", 9.20, 4.65, 1.2, 0.7, 42, AMBER, True)
    bd.add_text(slide, "partial", 9.80, 4.90, 2.4, 0.28, 10, BODY)
    bd.add_footer(slide, 1)

    # 2 — scorecard
    slide = bd.blank(prs)
    bd.add_section(slide, "01", "Review response", "WHAT CHANGED")
    bd.add_header(
        slide,
        "REVIEW RESPONSE  ·  8 COMMENTS",
        "What changed, and what is still open",
        "Each row points to the slide/file with the new evidence.",
    )
    rows = [
        ["#", "Review comment", "Status", "Where"],
        ["1", "Full epochs + validation loss", "Partial", "p3 (8 epochs; early stopping still open)"],
        ["2", "Per-appliance sample counts", "Closed", "p4"],
        ["3", "Class imbalance + microwave improvement", "Partial", "p5 (25× weighting is offline)"],
        ["4", "Architecture / ML diagram", "Closed", "p6"],
        ["5", "More F1 models, incl. State F1", "Partial", "p7 (3 models; no Seq2Seq yet)"],
        ["6", "Explain baseline / WHITED 44.1%", "Closed", "p8–p9"],
        ["7", "Real values behind red circles", "Closed", "p8"],
        ["8", "Dynamic demo", "Partial", "p10 (runbook, no recording)"],
    ]
    add_table(slide, rows, 4.55, 1.72, 8.08, 4.55, [0.45, 3.30, 1.05, 3.28], font_size=9)
    bd.add_callout(
        slide,
        "New since the review: 3-model MSE ablation, 2×2 loss ablation, house-2 cross-house, RMSE + block bootstrap CI, WHITED 40-class distribution, 25× microwave experiment.",
        4.55,
        6.45,
        8.10,
        0.55,
        size=9.2,
    )
    bd.add_footer(slide, 2)

    # 3 — training
    slide = bd.blank(prs)
    bd.add_section(slide, "02", "Training", "COMMENT 1")
    bd.add_header(
        slide,
        "FULL 8-EPOCH CYCLE",
        "Train and validation loss, every epoch",
        "The earlier deck showed only 3 epochs and no validation loss.",
    )
    bd.add_figure(slide, FIGS / "fig_training_all.png", 4.55, 1.70, 8.08, 3.85)
    bd.add_text(slide, "8 epochs  ·  5 appliances  ·  validation loss computed every epoch", 4.55, 5.66, 8.0, 0.25, 9, MUTED)
    bd.add_callout(
        slide,
        "Full 8-epoch cycle and validation curves are now shown. Validation stops improving on several appliances, but automatic early stopping is not implemented yet — hence 'partial'.",
        4.55,
        6.02,
        8.10,
        0.75,
        fill=RGBColor(0xFF, 0xF3, 0xD6),
        color=RGBColor(0x8A, 0x5B, 0x00),
        size=10.3,
        bold=True,
    )
    bd.add_footer(slide, 3)

    # 4 — sample counts / imbalance
    slide = bd.blank(prs)
    bd.add_section(slide, "03", "Data", "COMMENTS 2–3")
    bd.add_header(
        slide,
        "SAMPLE COUNTS  ·  CLASS IMBALANCE",
        "Rare classes, counted",
        "UK-DALE: 5 target appliances. WHITED: 40 classes, 18 evaluable.",
    )
    bd.add_figure(slide, FIGS / "fig_imbalance.png", 4.55, 1.72, 4.15, 2.05)
    for index, (number, label) in enumerate(
        [("0.39%", "microwave ON"), ("34", "positive test windows"), ("17 h", "ON in six months")]
    ):
        bd.add_stat(slide, number, label, 4.55 + index * 1.40, 4.02, 1.30, 0.72, number_size=15)
    bd.add_figure(slide, FIGS / "fig_whited_classes.png", 8.95, 1.72, 3.68, 4.50)
    bd.add_callout(
        slide,
        "Microwave is ON only 0.39% of the time; 22 of 40 WHITED classes have only one device, so they cannot be tested at all.",
        4.55,
        6.30,
        8.08,
        0.62,
        size=9.8,
    )
    bd.add_footer(slide, 4)

    # 5 — microwave improvement
    slide = bd.blank(prs)
    bd.add_section(slide, "03", "Data", "COMMENT 3")
    bd.add_header(
        slide,
        "MICROWAVE  ·  TARGETED FIX",
        "Why it fails, and one fix that works",
        "The problem is recall, not the operating point.",
    )
    bd.add_figure(slide, FIGS / "fig_threshold.png", 4.55, 1.70, 7.90, 3.65)
    stat_row(
        slide,
        [("0.407", "attention Event F1"), ("0.494", "25× weighted MSE"), ("0.68", "recall after fix")],
        y=5.55,
        h=0.65,
    )
    bd.add_callout(
        slide,
        "25× positive-weighted MSE raises Event F1 0.407→0.494 and recall 0.43→0.68, precision roughly flat; MAE rises 5.91→6.97 W. Offline only, not yet deployed.",
        4.55,
        6.32,
        8.10,
        0.60,
        fill=PALE_RED,
        color=RGBColor(0x99, 0x1B, 0x1B),
        size=9.8,
        bold=True,
    )
    bd.add_footer(slide, 5)

    # 6 — architecture
    slide = bd.blank(prs)
    bd.add_section(slide, "04", "Model", "COMMENT 4")
    bd.add_header(
        slide,
        "ARCHITECTURE  ·  BASELINE / ATTENTION",
        "Inside the models",
        "Input, kernel sizes, dilation rates, attention flow and output.",
    )
    # headers
    bd.add_text(slide, "Baseline CNN", 4.55, 1.62, 3.45, 0.28, 13, NAVY, True)
    bd.add_text(slide, "Attention (proposed)", 8.35, 1.62, 3.45, 0.28, 13, TEAL_DARK, True)
    bd.add_text(slide, "30.7M params", 4.55, 1.90, 3.35, 0.20, 8.2, MUTED)
    bd.add_text(slide, "9.8M params", 8.35, 1.90, 3.35, 0.20, 8.2, MUTED)

    def box(x, y, w, text, fill=LIGHT, border=BORDER, color=NAVY, size=8.2):
        bd.add_rect(slide, x, y, w, 0.40, fill, border, radius=0.1)
        bd.add_text(slide, text, x + 0.08, y, w - 0.16, 0.40, size, color, True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    def arrow(x, y):
        bd.add_rect(slide, x, y, 0.14, 0.08, BORDER, radius=0.2, shape=bd.MSO_SHAPE.DOWN_ARROW)

    baseline = ["(1 × 599) input", "5 × Conv1D k=5 · 30→50", "Flatten 50×599 → FC 1024", "Output 1"]
    for i, text in enumerate(baseline):
        y = 2.16 + i * 0.62
        box(4.55, y, 3.45, text)
        if i < 3:
            arrow(6.20, y + 0.42)
    bd.add_text(slide, "standard Seq2Point baseline", 4.55, 4.74, 3.45, 0.22, 8, MUTED)

    attention = [
        "(1 × 599) input",
        "Stem Conv1D k=5 · 32",
        "4 × DilatedBlock k=5 · d=1/2/4/8",
        "Channel SE · 32→8→32",
        "Temporal attention · k=1 → softmax",
        "FC 512 → output 1",
    ]
    for i, text in enumerate(attention):
        y = 2.16 + i * 0.58
        box(8.35, y, 3.45, text, fill=PALE_GREEN, border=RGBColor(0x9A, 0xD8, 0xCE), color=TEAL_DARK, size=7.9)
        if i < 5:
            arrow(10.00, y + 0.42)

    bd.add_rect(slide, 4.55, 5.55, 7.25, 0.52, RGBColor(0xFF, 0xF8, 0xE6), RGBColor(0xF2, 0xD8, 0x9A), radius=0.1)
    bd.add_text(
        slide,
        "WHITED baseline: 44.1 kHz current → 120 ms window → 19 features → Random Forest 400 trees → class / top-3",
        4.70,
        5.55,
        7.0,
        0.52,
        8.8,
        RGBColor(0x8A, 0x5B, 0x00),
        True,
        anchor=1,
    )
    bd.add_text(slide, "Dilation alone is not enough; attention adds the gain, but baseline still wins State F1.", 4.55, 6.35, 8.0, 0.25, 8.5, MUTED)
    bd.add_footer(slide, 6)

    # 7 — F1
    slide = bd.blank(prs)
    bd.add_section(slide, "05", "Results", "COMMENT 5")
    bd.add_header(
        slide,
        "EVENT F1 + STATE F1  ·  THREE MODELS",
        "More than one model, more than one F1",
        "Same MSE loss, same 8 epochs, same seed; no Seq2Seq yet.",
    )
    bd.add_figure(slide, FIGS / "fig_metrics.png", 4.55, 1.70, 8.08, 3.75)
    bd.add_callout(
        slide,
        "Attention: Event 0.797 / State 0.762. Baseline: Event 0.789 / State 0.790. Dilated: 0.786 / 0.733. Attention wins MAE and Event, baseline wins State; the difference is not universal.",
        4.55,
        5.62,
        8.10,
        0.85,
        size=10.2,
    )
    bd.add_text(slide, "Cross-house: attention 0.775 vs baseline 0.814 Event F1 — see p9.", 4.57, 6.55, 8.0, 0.22, 8.5, MUTED)
    bd.add_footer(slide, 7)

    # 8 — red circles
    slide = bd.blank(prs)
    bd.add_section(slide, "05", "Results", "COMMENT 6")
    bd.add_header(
        slide,
        "REAL VALUES  ·  RED CIRCLES",
        "What the red circles actually show",
        "Total power is high while the model output is near zero.",
    )
    bd.add_figure(slide, FIGS / "fig_failure.png", 4.55, 1.70, 8.08, 3.85)
    bd.add_callout(
        slide,
        "90–120 min: dishwasher truth ~1.1 kW, model ~0.2 kW. Average residual is only 174 W, so this is a recall failure, not an unmeasured appliance.",
        4.55,
        5.68,
        8.10,
        0.78,
        fill=PALE_RED,
        color=RGBColor(0x99, 0x1B, 0x1B),
        size=10.5,
        bold=True,
    )
    bd.add_footer(slide, 8)

    # 9 — why numbers
    slide = bd.blank(prs)
    bd.add_section(slide, "06", "Interpretation", "COMMENT 6")
    bd.add_header(
        slide,
        "WHY THE CLAIMS ARE CONDITIONAL",
        "Why the numbers are what they are",
        "UK-DALE trade-off; WHITED long tail; neither is a clean win.",
    )
    bd.add_figure(slide, FIGS / "fig_cross_house.png", 4.55, 1.75, 4.35, 3.30)
    bd.add_rect(slide, 9.10, 1.75, 3.55, 1.95, LIGHT, BORDER, radius=0.08)
    bd.add_text(slide, "UK-DALE", 9.28, 1.90, 3.0, 0.28, 12, RED, True)
    bd.add_text(
        slide,
        "• Attention wins MAE/Event; baseline wins State.\n• Cross-house ranking flips (0.814 vs 0.775).\n• No universal 'better model' claim.",
        9.28,
        2.25,
        3.15,
        1.35,
        8.8,
        BODY,
    )
    bd.add_rect(slide, 9.10, 3.90, 3.55, 2.05, LIGHT, BORDER, radius=0.08)
    bd.add_text(slide, "WHITED", 9.28, 4.05, 3.0, 0.28, 12, TEAL_DARK, True)
    bd.add_text(
        slide,
        "• 44.1% top-1, 71.8% top-3.\n• 22/40 classes cannot be tested.\n• Confusions are physically similar loads.",
        9.28,
        4.40,
        3.15,
        1.35,
        8.8,
        BODY,
    )
    bd.add_callout(
        slide,
        "What would change the conclusion: Seq2Seq baseline, early stopping, 3-seed repeats, and a cross-dataset test.",
        4.55,
        5.95,
        8.10,
        0.72,
        fill=PALE_RED,
        color=RGBColor(0x99, 0x1B, 0x1B),
        size=10.5,
        bold=True,
    )
    bd.add_footer(slide, 9)

    # 10 — demo
    slide = bd.blank(prs)
    bd.add_section(slide, "07", "Demo", "COMMENT 7")
    bd.add_header(
        slide,
        "LIVE DEMO  ·  4 SCENES",
        "Demo: four scenes, one API",
        "Runbook prepared; no recording yet.",
    )
    bd.add_figure(slide, SHOTS / "web_dashboard_tall.png", 4.55, 1.70, 4.85, 3.75, pad=0.04)
    steps = [
        ("1", "Login / select building", "Building A · UK-DALE House 1"),
        ("2", "Replay ON/OFF", "start replay; watch fridge/kettle cards"),
        ("3", "Evaluation / Analytics", "F1, bill, unmetered, alert log"),
        ("4", "Mobile H5", "same API, English-only UI"),
    ]
    for index, (number, title, detail) in enumerate(steps):
        y = 1.80 + index * 1.12
        bd.add_rect(slide, 9.70, y, 0.34, 0.34, TEAL, radius=0.5, shape=bd.MSO_SHAPE.OVAL)
        bd.add_text(slide, number, 9.70, y + 0.04, 0.34, 0.20, 9, WHITE, True, align=PP_ALIGN.CENTER)
        bd.add_text(slide, title, 10.15, y, 2.5, 0.28, 10.5, NAVY, True)
        bd.add_text(slide, detail, 10.15, y + 0.27, 2.55, 0.30, 8.2, BODY)
    bd.add_callout(
        slide,
        "Rehearse 12/1–12/6; fallback screenshots are in report_build/shots. Runbook: NILM/DEMO_RUNBOOK.md.",
        4.55,
        5.70,
        8.10,
        0.55,
        size=9.5,
    )
    bd.add_footer(slide, 10)

    # 11 — next 6 days
    slide = bd.blank(prs)
    bd.add_section(slide, "08", "Next", "6 DAYS")
    bd.add_header(
        slide,
        "25 NOV → 07 DEC",
        "Next 6 days: freeze evidence, write, rehearse",
        "No new experiments before 11/30.",
    )
    rows = [
        ["Date", "Deliverable", "Owner", "Done when"],
        ["11/25", "Professor meeting: review response + scope decisions", "All", "Decisions recorded"],
        ["11/25–11/27", "Report §1–§5: baseline, changes, design, implementation, validation", "Jin/Yang", "Draft v0.8"],
        ["11/28", "Report §6–§8, Gantt, team contributions, internal review", "All", "Draft v0.9"],
        ["11/29", "QA: commits, numbers, page limits, WEMUST upload", "Jin", "Final PDF + receipt"],
        ["11/30", "Submit Progress Report via WEMUST", "Jin", "Submission receipt"],
        ["12/01–12/06", "10-min oral deck + 5-min Q&A + demo rehearsal", "All", "Recorded run-through"],
        ["12/07", "Oral report", "All", "15 points"],
    ]
    add_table(slide, rows, 4.55, 1.72, 8.08, 4.45, [1.05, 4.45, 1.25, 1.33], font_size=8.8, status_col=None)
    bd.add_callout(
        slide,
        "Report rule: every number points to a commit/tag; every unfinished item has a week; every scope change has reason + impact + advisor confirmation.",
        4.55,
        6.35,
        8.10,
        0.58,
        size=9.2,
    )
    bd.add_footer(slide, 11)

    # 12 — next 8 weeks
    slide = bd.blank(prs)
    bd.add_section(slide, "08", "Next", "8 WEEKS")
    bd.add_header(
        slide,
        "AFTER THE MIDTERM",
        "What to do after the midterm",
        "Close the proposal gaps in this order; do not add features first.",
    )
    rows = [
        ["Workstream", "What", "Why / proposal gap", "By", "Owner"],
        ["Evidence", "Seq2Seq baseline; early stopping; 3 seeds mean±SD; REDD/PLAID", "O3/O4/O5; missing comparison and generalization", "15 Jan", "Yang"],
        ["System", "Redis/Postgres decision; Modbus/MQTT; self-contained Docker; pytest/CI/Alembic", "O6/O7; current Redis/Modbus are stubs", "15 Jan", "Jin"],
        ["Thesis", "Results chapter, figures, Gantt, limitations", "Final report; current draft is deck-only", "31 Mar", "All"],
        ["Delivery", "Final report, defense deck, live demo", "Final submission", "Apr–May", "All"],
    ]
    add_table(slide, rows, 4.55, 1.72, 8.08, 3.55, [1.25, 3.15, 2.45, 0.65, 0.58], font_size=8.3, status_col=None)
    bd.add_callout(
        slide,
        "Decision needed: (1) report structure 8 chapters vs BIT 6 sections; (2) REDD/PLAID vs WHITED CNN; (3) Redis/Modbus scope; (4) live demo vs recorded fallback.",
        4.55,
        5.55,
        8.10,
        1.02,
        fill=PALE_GREEN,
        color=TEAL_DARK,
        size=9.8,
        bold=True,
    )
    bd.add_footer(slide, 12)

    # 13 — decisions
    slide = bd.blank(prs)
    bd.add_rect(slide, 0.72, 0.72, 11.90, 6.05, TEAL, radius=0, shape=bd.MSO_SHAPE.RECTANGLE)
    bd.add_text(slide, "THREE DECISIONS TODAY", 1.15, 1.35, 11.0, 0.32, 10, WHITE, True, spacing=140)
    bd.add_text(slide, "What we need from you", 1.15, 1.85, 11.0, 0.9, 34, WHITE, True)
    decisions = [
        ("1", "Report structure", "8 chapters from Lecture 4, or strict BIT 6-section template?"),
        ("2", "Scope", "REDD/PLAID vs WHITED CNN; Redis/Modbus now or after midterm?"),
        ("3", "Demo", "Live interactive demo or recorded fallback for 12/07?"),
    ]
    for index, (number, title, detail) in enumerate(decisions):
        y = 3.20 + index * 0.95
        bd.add_rect(slide, 1.15, y, 0.40, 0.40, WHITE, radius=0.5, shape=bd.MSO_SHAPE.OVAL)
        bd.add_text(slide, number, 1.15, y + 0.06, 0.40, 0.22, 11, TEAL_DARK, True, align=PP_ALIGN.CENTER)
        bd.add_text(slide, title, 1.75, y - 0.02, 2.0, 0.30, 15, WHITE, True)
        bd.add_text(slide, detail, 3.75, y - 0.02, 8.2, 0.32, 12, WHITE)
    bd.add_text(slide, "Questions?", 1.15, 6.15, 4.0, 0.5, 24, WHITE, True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"wrote {OUT} with {len(prs.slides)} slides")


if __name__ == "__main__":
    build()
