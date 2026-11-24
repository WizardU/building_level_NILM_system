"""Build the bi-weekly NILM progress deck in the style of NILM-pre10.21.pptx."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计")
BASE = Path(__file__).resolve().parent
FIGS = BASE / "figs"
SHOTS = BASE / "shots"
OUT = ROOT / "NILM-pre11.25.pptx"

FONT = "Corbel"
TEAL = RGBColor(0x40, 0xBA, 0xD2)
TEAL_DARK = RGBColor(0x16, 0x60, 0x6B)
TEAL_MID = RGBColor(0x1A, 0xB3, 0x9F)
LIGHT = RGBColor(0xEA, 0xF7, 0xFA)
BORDER = RGBColor(0xBF, 0xE5, 0xEE)
NAVY = RGBColor(0x14, 0x33, 0x3D)
BODY = RGBColor(0x47, 0x55, 0x69)
MUTED = RGBColor(0x7B, 0x8A, 0x99)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY_BG = RGBColor(0xF1, 0xF3, 0xF4)
ORANGE = RGBColor(0xEE, 0x70, 0x08)
AMBER = RGBColor(0xFA, 0xB9, 0x00)
GREEN = RGBColor(0x1A, 0xB3, 0x9F)
RED = RGBColor(0xD5, 0x39, 0x3D)
PALE_RED = RGBColor(0xFD, 0xEC, 0xEC)
PALE_GREEN = RGBColor(0xE8, 0xF8, 0xF2)

TOTAL = 15
_footer_page = 0


def rgb(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value)


def add_footer(slide, page=None):
    global _footer_page
    _footer_page += 1
    add_text(
        slide,
        f"NILM progress report  ·  25 Nov 2026  ·  {_footer_page:02d}",
        8.4,
        7.12,
        4.4,
        0.22,
        8,
        MUTED,
        align=PP_ALIGN.RIGHT,
    )


def add_rect(
    slide,
    x,
    y,
    w,
    h,
    fill,
    line=None,
    radius=0.08,
    shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    line_width=0.75,
):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_width)
    shp.shadow.inherit = False
    return shp


def add_text(
    slide,
    text,
    x,
    y,
    w,
    h,
    size=14,
    color=NAVY,
    bold=False,
    align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP,
    font=FONT,
    line_spacing=1.0,
    space_after=0,
    italic=False,
    spacing=None,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    frame.vertical_anchor = anchor
    for index, line in enumerate(text.split("\n")):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.alignment = align
        paragraph.line_spacing = line_spacing
        paragraph.space_after = Pt(space_after)
        run = paragraph.add_run()
        run.text = line
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
        if spacing:
            try:
                run.font._rPr.set("spc", str(spacing))
            except Exception:
                pass
    return box


def add_picture_fit(slide, path, x, y, w, h):
    with Image.open(path) as image:
        iw, ih = image.size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    px, py = x + (w - pw) / 2, y + (h - ph) / 2
    return slide.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(pw), Inches(ph))


def add_figure(slide, path, x, y, w, h, pad=0.08):
    add_rect(slide, x, y, w, h, WHITE, BORDER, radius=0.03)
    return add_picture_fit(slide, path, x + pad, y + pad, w - 2 * pad, h - 2 * pad)


def add_section(slide, number, title, kicker):
    add_rect(slide, 0, 0.62, 4.12, 6.26, TEAL, radius=0.0, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, number, 0.45, 1.45, 1.2, 0.5, 12, WHITE, True, spacing=120)
    add_text(slide, title, 0.45, 1.95, 3.2, 2.0, 30, WHITE, True, line_spacing=0.95)
    add_text(slide, kicker, 0.47, 4.25, 3.2, 0.5, 10, WHITE, False, spacing=160)
    add_text(slide, "NILM  /  BUILDING ENERGY", 0.47, 6.35, 3.2, 0.3, 8, WHITE)


def add_header(slide, kicker, title, subtitle=None):
    add_text(slide, kicker, 4.55, 0.52, 8.2, 0.3, 9, TEAL_DARK, True, spacing=140)
    add_text(slide, title, 4.55, 0.76, 8.2, 0.7, 27, NAVY, True, line_spacing=0.95)
    if subtitle:
        add_text(slide, subtitle, 4.57, 1.42, 8.1, 0.35, 11.5, MUTED)


def add_callout(slide, text, x, y, w, h, fill=LIGHT, color=NAVY, size=12, bold=False):
    add_rect(slide, x, y, w, h, fill, BORDER, radius=0.12)
    add_text(slide, text, x + 0.25, y, w - 0.5, h, size, color, bold, anchor=MSO_ANCHOR.MIDDLE)


def add_stat(slide, number, label, x, y, w, h=0.95, accent=TEAL_DARK, number_size=28):
    add_rect(slide, x, y, w, h, LIGHT, BORDER, radius=0.1)
    add_text(slide, number, x + 0.18, y + 0.08, w - 0.36, 0.5, number_size, accent, True)
    add_text(slide, label, x + 0.18, y + h - 0.34, w - 0.36, 0.3, 9.5, MUTED)


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def build() -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    prs.core_properties.title = "Building-Level NILM System - Progress Report"
    prs.core_properties.author = "JinXinyi, YangYifei, YuShengbin"

    metrics_rows = json.loads(
        (BASE.parent / "ml/checkpoints/ablation_metrics.json").read_text(encoding="utf-8")
    )

    def metric(appliance: str, model: str, key: str) -> float:
        return float(
            next(
                r[key]
                for r in metrics_rows
                if r["appliance"] == appliance
                and r["model"] == model
                and r.get("loss") == "mse"
            )
        )

    def mean_metric(model: str, key: str) -> float:
        values = [
            r[key]
            for r in metrics_rows
            if r["model"] == model and r.get("loss") == "mse"
        ]
        return float(sum(values) / len(values))

    # 1 — Title
    slide = blank(prs)
    add_rect(slide, 0, 0.72, 8.45, 6.05, TEAL, radius=0, shape=MSO_SHAPE.RECTANGLE)
    add_rect(slide, 8.95, 0.72, 3.85, 6.05, GREY_BG, radius=0, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, "BI-WEEKLY REPORT  ·  25 NOV 2026", 0.78, 1.18, 6.8, 0.3, 10, WHITE, True, spacing=120)
    add_text(slide, "Building-Level\nNILM System", 0.78, 1.72, 7.1, 1.9, 38, WHITE, True, line_spacing=0.92)
    add_text(slide, "Two-Week Progress Report", 0.80, 3.78, 6.8, 0.4, 19, WHITE)
    add_text(slide, "JinXinyi   ·   YangYifei   ·   YuShengbin", 0.80, 4.48, 6.8, 0.3, 13, WHITE)
    add_text(
        slide,
        "Real data   ·   trained models   ·   working Web & mobile apps",
        0.80,
        5.92,
        7.0,
        0.35,
        11,
        WHITE,
    )
    add_text(slide, "ONE METER", 9.22, 1.12, 3.2, 0.25, 9, MUTED, True, spacing=120)
    add_text(slide, "1", 9.18, 1.35, 1.0, 0.9, 54, TEAL_DARK, True)
    add_text(slide, "whole-home signal", 9.24, 2.22, 3.2, 0.25, 9.5, BODY)
    add_picture_fit(slide, FIGS / "fig_spark.png", 9.20, 2.55, 3.35, 0.82)
    add_text(slide, "5", 9.18, 3.55, 1.0, 0.9, 54, TEAL_DARK, True)
    add_text(slide, "appliances recovered", 9.24, 4.42, 3.2, 0.25, 9.5, BODY)
    add_text(
        slide,
        "Fridge · Kettle · Microwave\nDishwasher · Washing machine",
        9.22,
        4.78,
        3.3,
        0.55,
        9,
        BODY,
        line_spacing=1.1,
    )
    add_text(slide, "From one signal to five stories.", 9.22, 5.95, 3.3, 0.3, 10, TEAL_DARK, True, italic=True)
    add_footer(slide, 1)

    # 2 — What is NILM
    slide = blank(prs)
    add_section(slide, "01", "The idea", "WHAT IS NILM?")
    add_header(
        slide,
        "THE PROBLEM",
        "One meter. Every appliance.",
        "Non-Intrusive Load Monitoring: no extra sensor on each device.",
    )
    add_rect(slide, 4.55, 1.92, 2.25, 2.55, RGBColor(0xF8, 0xFA, 0xFC), RGBColor(0xCB, 0xD5, 0xE1), radius=0.04)
    add_text(slide, "BUILDING", 4.75, 2.08, 1.8, 0.25, 8.5, MUTED, True, spacing=100)
    for row in range(3):
        for col in range(2):
            add_rect(slide, 4.83 + col * 0.82, 2.50 + row * 0.52, 0.55, 0.34, BORDER, radius=0.05)
    meter = add_rect(slide, 5.43, 4.12, 0.55, 0.55, AMBER, radius=0.5, shape=MSO_SHAPE.OVAL)
    add_text(slide, "M", 5.43, 4.20, 0.55, 0.3, 13, WHITE, True, align=PP_ALIGN.CENTER)
    add_text(slide, "one meter, at the main switch", 4.55, 4.78, 2.3, 0.3, 9, MUTED, align=PP_ALIGN.CENTER)
    add_rect(slide, 7.02, 3.12, 0.82, 0.32, BORDER, radius=0.2, shape=MSO_SHAPE.RIGHT_ARROW)
    add_text(slide, "software", 7.02, 2.88, 0.85, 0.22, 8, MUTED, align=PP_ALIGN.CENTER)

    chips = [
        ("Fridge", "120 W", "2E86AB"),
        ("Kettle", "1.8 kW", "EE7008"),
        ("Microwave", "1.2 kW", "D5393D"),
        ("Dishwasher", "0.9 kW", "90BB23"),
        ("Washing machine", "0.5 kW", "7C5CBF"),
    ]
    for index, (name, power, color) in enumerate(chips):
        y = 1.92 + index * 0.67
        add_rect(slide, 8.06, y, 2.55, 0.55, LIGHT, BORDER, radius=0.12)
        add_rect(slide, 8.06, y, 0.08, 0.55, rgb(color), radius=0, shape=MSO_SHAPE.RECTANGLE)
        add_text(slide, name, 8.26, y + 0.06, 1.5, 0.25, 10.5, NAVY, True)
        add_text(slide, power, 10.0, y + 0.08, 0.6, 0.25, 9, MUTED, align=PP_ALIGN.RIGHT)
    add_text(slide, "typical power", 10.60, 5.42, 0.9, 0.22, 8, MUTED, align=PP_ALIGN.RIGHT)
    add_callout(
        slide,
        "The meter sees one number. Software learns each appliance's signature and splits it back out.",
        4.55,
        5.72,
        8.10,
        0.92,
        size=12,
        bold=False,
    )
    add_footer(slide, 2)

    # 3 — This period
    slide = blank(prs)
    add_section(slide, "02", "This period", "WHAT CHANGED")
    add_header(slide, "TWO WEEKS", "Demo to real system", "The end-to-end path is now running on real data.")
    stats = [
        ("2.6 M", "measurements"),
        ("5", "appliances"),
        ("10", "ONNX models"),
        ("21", "API checks"),
    ]
    for index, (number, label) in enumerate(stats):
        add_stat(slide, number, label, 4.55 + index * 2.08, 1.78, 1.95, 1.15, number_size=30)
    add_text(slide, "WEEK 1", 4.58, 3.35, 2.0, 0.25, 8.5, MUTED, True, spacing=100)
    add_text(slide, "WEEK 2", 9.60, 3.35, 2.0, 0.25, 8.5, MUTED, True, spacing=100)
    add_rect(slide, 4.75, 3.93, 7.7, 0.035, RGBColor(0xCB, 0xD5, 0xE1), radius=0, shape=MSO_SHAPE.RECTANGLE)
    steps = [
        ("1", "Real data", "UK-DALE"),
        ("2", "Train", "5 appliances"),
        ("3", "Export", "ONNX"),
        ("4", "Apps", "Web + mobile"),
        ("5", "Second set", "WHITED"),
    ]
    for index, (number, title, detail) in enumerate(steps):
        x = 4.62 + index * 1.60
        add_rect(slide, x, 3.79, 0.32, 0.32, TEAL, radius=0.5, shape=MSO_SHAPE.OVAL)
        add_text(slide, number, x, 3.83, 0.32, 0.20, 9, WHITE, True, align=PP_ALIGN.CENTER)
        add_text(slide, title, x - 0.08, 4.34, 1.45, 0.28, 10, NAVY, True)
        add_text(slide, detail, x - 0.08, 4.64, 1.45, 0.28, 8.5, MUTED)
    fixes = [
        ("FIXED", "cache · timezone · duplicate rows"),
        ("CLEANED", "legacy code · stale OpenAPI"),
        ("ADDED", "WHITED · 21 API checks"),
    ]
    for index, (tag, detail) in enumerate(fixes):
        x = 4.55 + index * 2.72
        add_rect(slide, x, 5.02, 2.58, 0.58, WHITE, BORDER, radius=0.1)
        add_text(slide, tag, x + 0.16, 5.02, 0.9, 0.58, 7.5, TEAL_DARK, True, spacing=80, anchor=MSO_ANCHOR.MIDDLE)
        add_text(slide, detail, x + 0.95, 5.02, 1.55, 0.58, 8.2, BODY, anchor=MSO_ANCHOR.MIDDLE)
    add_callout(
        slide,
        "Before: a synthetic demo.  Now: real UK-DALE data, trained models, and both apps running end to end.",
        4.55,
        5.82,
        8.10,
        0.78,
        fill=PALE_GREEN,
        color=TEAL_DARK,
        size=11,
        bold=True,
    )
    add_footer(slide, 3)

    # 4 — Data
    slide = blank(prs)
    add_section(slide, "03", "Data", "REAL MEASUREMENTS")
    add_header(
        slide,
        "UK-DALE  ·  HOUSE 1",
        "What the meter actually sees",
        "Six months of one home; one reading every six seconds.",
    )
    add_figure(slide, FIGS / "fig_day.png", 4.55, 1.72, 8.08, 4.30)
    for index, (number, label) in enumerate(
        [("180", "days of data"), ("2,606,400", "measurements"), ("5", "appliances")]
    ):
        add_stat(slide, number, label, 4.55 + index * 2.70, 6.05, 2.55, 0.78, number_size=15)
    add_footer(slide, 4)

    # 5 — Class imbalance
    slide = blank(prs)
    add_section(slide, "03", "Data", "WHO IS RARE?")
    add_header(
        slide,
        "CLASS BALANCE  ·  SIX MONTHS",
        "The microwave is barely there",
        "Share of time ON; positive windows in the 13,013-window test split.",
    )
    add_figure(slide, FIGS / "fig_imbalance.png", 4.55, 1.76, 8.08, 3.20)
    for index, (number, label) in enumerate(
        [("0.39%", "microwave ON"), ("34", "positive test windows"), ("17 h", "ON in six months")]
    ):
        add_stat(slide, number, label, 4.55 + index * 2.70, 5.08, 2.55, 0.78, number_size=20)
    add_callout(
        slide,
        "A model that always predicts OFF is right 99.6% of the time. That is why we report F1, not accuracy.",
        4.55,
        6.02,
        8.10,
        0.82,
        fill=PALE_RED,
        color=RGBColor(0x99, 0x1B, 0x1B),
        size=11.5,
        bold=True,
    )
    add_footer(slide, 5)

    # 6 — Training curves
    slide = blank(prs)
    add_section(slide, "04", "Model", "ALL EPOCHS")
    add_header(
        slide,
        "TRAINING  ·  EVERY EPOCH",
        "Train loss falls. Validation flattens.",
        "Five appliances; attention model; validation loss computed every epoch.",
    )
    add_figure(slide, FIGS / "fig_training_all.png", 4.55, 1.76, 8.08, 3.82)
    add_text(
        slide,
        "Per-epoch values, not a smoothed summary. The final ON threshold is calibrated on validation, never on test.",
        4.55,
        5.68,
        8.10,
        0.28,
        8.7,
        MUTED,
    )
    add_callout(
        slide,
        "Training loss keeps falling; validation loss stops improving after the first few epochs on several appliances. Early stopping is the next step.",
        4.55,
        6.02,
        8.10,
        0.82,
        size=11.5,
    )
    add_footer(slide, 6)

    # 7 — Model architectures
    slide = blank(prs)
    add_section(slide, "04", "Model", "INSIDE")
    add_header(
        slide,
        "BASELINE VS ATTENTION",
        "Inside the model",
        "Same 599-sample input and one output; different ways to focus on the signal.",
    )

    def params_of(model_name: str) -> int:
        path = BASE.parent / f"ml/checkpoints/fridge_{model_name}.json"
        try:
            return int(json.loads(path.read_text(encoding="utf-8")).get("params", 0))
        except Exception:
            return 0

    def arch_box(x, y, w, text, fill=LIGHT, border=BORDER, size=8.8, color=NAVY):
        add_rect(slide, x, y, w, 0.46, fill, border, radius=0.1)
        add_text(slide, text, x + 0.10, y, w - 0.20, 0.46, size, color, True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    def down_arrow(x, y):
        add_rect(slide, x, y, 0.16, 0.09, BORDER, radius=0.2, shape=MSO_SHAPE.DOWN_ARROW)

    left_x, right_x = 4.55, 8.62
    col_w = 3.70
    add_text(slide, "Baseline CNN", left_x, 1.62, col_w, 0.28, 14, NAVY, True)
    add_text(slide, f"{params_of('baseline')/1e6:.1f}M params", left_x, 1.90, col_w, 0.22, 8.5, MUTED)
    add_text(slide, "Attention (proposed)", right_x, 1.62, col_w, 0.28, 14, TEAL_DARK, True)
    add_text(slide, f"{params_of('attention')/1e6:.1f}M params", right_x, 1.90, col_w, 0.22, 8.5, MUTED)

    baseline = [
        "Input  ·  (1 × 599)",
        "5 × Conv1D  ·  k=5, 30→50 filters",
        "Flatten  ·  50 × 599 → FC 1024",
        "Output  ·  one power value",
    ]
    for index, text in enumerate(baseline):
        y = 2.22 + index * 0.72
        arch_box(left_x, y, col_w, text)
        if index < len(baseline) - 1:
            down_arrow(left_x + col_w / 2 - 0.08, y + 0.48)
    add_text(slide, "Standard Seq2Point baseline", left_x, 5.02, col_w, 0.25, 9, MUTED)

    attention = [
        "Input  ·  (1 × 599)",
        "Stem Conv1D  ·  k=5, 32 filters",
        "4 × DilatedBlock  ·  k=5, d=1/2/4/8",
        "Channel attention  ·  32→8→32",
        "Temporal attention  ·  Conv1d k=1 → softmax",
        "FC 512  →  output 1",
        "Output  ·  one power value",
    ]
    for index, text in enumerate(attention):
        y = 2.22 + index * 0.55
        arch_box(
            right_x,
            y,
            col_w,
            text,
            fill=PALE_GREEN,
            border=RGBColor(0x9A, 0xD8, 0xCE),
            color=TEAL_DARK,
            size=8.6,
        )
        if index < len(attention) - 1:
            down_arrow(right_x + col_w / 2 - 0.08, y + 0.48)

    add_callout(
        slide,
        f"Same input, output and loss; attention is smaller ({params_of('attention')/1e6:.1f}M vs {params_of('baseline')/1e6:.1f}M) and learns which channels and time regions matter.",
        4.55,
        6.30,
        8.10,
        0.60,
        size=10.5,
        bold=False,
    )
    add_footer(slide, 7)

    # 8 — Results
    slide = blank(prs)
    att_event = mean_metric("attention", "event_f1")
    base_event = mean_metric("baseline", "event_f1")
    dil_event = mean_metric("dilated", "event_f1")
    att_state = mean_metric("attention", "state_f1")
    att_mae = mean_metric("attention", "mae")
    add_section(slide, "05", "Results", "DOES IT WORK?")
    add_header(
        slide,
        "TEST SET  ·  13,013 WINDOWS PER APPLIANCE",
        "Good on four. Weak on one.",
        f"Event F1: attention {att_event:.2f}, baseline {base_event:.2f}, dilated {dil_event:.2f}.",
    )
    add_figure(slide, FIGS / "fig_metrics.png", 4.55, 1.72, 8.08, 3.95)
    for index, (number, label) in enumerate(
        [
            (f"{att_event:.2f}", "average event F1"),
            (f"{att_state:.2f}", "average state F1"),
            (f"{att_mae:.1f} W", "average MAE"),
        ]
    ):
        add_stat(slide, number, label, 4.55 + index * 2.70, 5.85, 2.55, 0.72, number_size=19)
    add_text(
        slide,
        "Dilation alone is not enough; attention gains event F1 and MAE, while baseline still wins state F1.",
        4.55,
        6.66,
        8.1,
        0.3,
        8.5,
        MUTED,
    )
    add_footer(slide, 8)

    # 9 — Threshold curves
    slide = blank(prs)
    add_section(slide, "05", "Results", "WHY MICROWAVE?")
    add_header(
        slide,
        "CLASS IMBALANCE  ·  THRESHOLD SWEEP",
        "Even the best threshold cannot fix recall.",
        "Microwave: 0.39% ON, 34 positive test windows, 17 h in six months.",
    )
    add_figure(slide, FIGS / "fig_threshold.png", 4.55, 1.76, 8.08, 3.90)
    add_callout(
        slide,
        "Threshold alone cannot fix recall. A 25× positive-weighted MSE lifts microwave Event F1 0.407→0.494 (recall 0.68, precision flat), with slightly higher MAE; next is event-level post-processing.",
        4.55,
        5.82,
        8.10,
        0.95,
        size=11,
    )
    add_footer(slide, 9)

    # 10 — Disaggregation estimates
    slide = blank(prs)
    add_section(slide, "05", "Results", "ONE WINDOW")
    add_header(
        slide,
        "TWO-HOUR EXAMPLE",
        "One signal in. Five estimates out.",
        "Measured mains (navy) versus model estimates (colours); estimates, not truth.",
    )
    add_figure(slide, FIGS / "fig_disagg.png", 4.55, 1.72, 8.08, 3.95)
    add_callout(
        slide,
        "The model tracks some events, but not all. The next slide compares the estimates with measured appliance power.",
        4.55,
        5.85,
        8.10,
        0.82,
        size=11.5,
    )
    add_footer(slide, 10)

    # 11 — Failure case
    slide = blank(prs)
    add_section(slide, "05", "Results", "ERROR ANALYSIS")
    add_header(
        slide,
        "THE RED CIRCLES, EXPLAINED",
        "Where the estimates fail",
        "Same window: total power is high while the model output is near zero.",
    )
    add_figure(slide, FIGS / "fig_failure.png", 4.55, 1.76, 8.08, 3.88)
    add_callout(
        slide,
        "90-120 min: dishwasher truth ~1.1 kW, model output far below. Average residual is only 174 W, so this is a recall failure, not an unmodeled appliance.",
        4.55,
        5.70,
        8.10,
        0.98,
        fill=PALE_RED,
        color=RGBColor(0x99, 0x1B, 0x1B),
        size=10.8,
        bold=True,
    )
    add_footer(slide, 11)

    # 8 — WHITED concept
    slide = blank(prs)
    add_section(slide, "06", "Second dataset", "WHITED")
    add_header(
        slide,
        "START-UP TRANSIENTS  ·  44.1 KHz",
        "Start-up fingerprints",
        "994 high-frequency switch-on recordings from 100 devices.",
    )
    add_figure(slide, FIGS / "fig_whited_waves.png", 4.55, 1.90, 8.08, 2.35)
    for index, (number, label) in enumerate(
        [("994", "recordings"), ("40", "appliance classes"), ("100", "devices")]
    ):
        add_stat(slide, number, label, 4.55 + index * 2.70, 4.42, 2.55, 0.78, number_size=20)
    add_callout(
        slide,
        "A 50 ms current transient is often enough to tell a kettle from a microwave - a second way to identify loads.",
        4.55,
        5.50,
        8.10,
        0.95,
        size=11.5,
        bold=False,
    )
    add_footer(slide, 8)

    # 9 — WHITED results
    slide = blank(prs)
    add_section(slide, "06", "Second dataset", "CAN WE NAME IT?")
    add_header(
        slide,
        "DEVICE-HOLD-OUT TEST",
        "Can we name the appliance?",
        "Strict test: 20 unseen devices; only 18 of 40 classes have more than one device.",
    )
    for index, (number, label) in enumerate(
        [("44.1%", "accuracy"), ("27.0%", "macro F1"), ("71.8%", "top-3 accuracy")]
    ):
        add_stat(slide, number, label, 4.55 + index * 2.70, 1.74, 2.55, 0.76, number_size=21)
    add_figure(slide, FIGS / "fig_whited_confusion.png", 4.55, 2.78, 7.85, 2.72)
    add_callout(
        slide,
        "Mistakes make physical sense: coffee machine / iron -> kettle (heating); laptop / monitor -> game console (power supply).",
        4.55,
        5.70,
        8.10,
        0.95,
        size=11,
    )
    add_text(slide, "This is a baseline, not a final result; a raw-waveform CNN is next.", 4.57, 6.72, 8.0, 0.22, 8.5, MUTED)
    add_footer(slide, 9)

    # 10 — WHITED class distribution + classifier
    slide = blank(prs)
    add_section(slide, "06", "Second dataset", "40 CLASSES")
    add_header(
        slide,
        "CLASS DISTRIBUTION  ·  RF BASELINE",
        "A long tail of start-ups",
        "18 classes are evaluable; 22 have only one device and stay train-only.",
    )
    add_figure(slide, FIGS / "fig_whited_classes.png", 4.55, 1.70, 4.25, 4.60)
    rf_steps = [
        "FLAC current channel  ·  44.1 kHz",
        "120 ms switch-on window",
        "19 time-frequency features",
        "Random Forest  ·  400 trees",
        "Class + top-3 prediction",
    ]
    for index, text in enumerate(rf_steps):
        y = 1.82 + index * 0.78
        add_rect(slide, 9.10, y, 3.55, 0.50, LIGHT, BORDER, radius=0.1)
        add_text(slide, text, 9.22, y, 3.30, 0.50, 9.2, NAVY, True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        if index < len(rf_steps) - 1:
            add_rect(slide, 10.78, y + 0.51, 0.18, 0.10, BORDER, radius=0.2, shape=MSO_SHAPE.DOWN_ARROW)
    add_callout(
        slide,
        "The long tail explains the 44.1% accuracy: 22 classes have only one device, so they cannot appear in the test set at all.",
        9.10,
        5.80,
        3.55,
        1.05,
        size=9.5,
    )
    add_text(slide, "This is the baseline classifier; a raw-waveform CNN is next.", 4.57, 6.45, 8.0, 0.22, 8.5, MUTED)
    add_footer(slide, 10)

    # 11 — Why the numbers are what they are
    slide = blank(prs)
    add_section(slide, "06", "Second dataset", "WHY?")
    add_header(
        slide,
        "CROSS-CHECK  ·  BOTH DATASETS",
        "Why the numbers are what they are",
        "Two datasets, two different reasons; neither is a clean win.",
    )
    cards = [
        (
            4.55,
            "UK-DALE  ·  house 1 → house 2",
            [
                "Attention wins MAE (−16.1%) and Event F1 (+0.008), but baseline wins State F1 (0.790 vs 0.762).",
                "Cross-house ranking flips: baseline 0.814 vs attention 0.775 Event F1.",
                "So: do not claim a universal 'better model'; report the trade-off.",
            ],
            RED,
        ),
        (
            8.65,
            "WHITED  ·  20 unseen devices",
            [
                "44.1% top-1, 71.8% top-3; 18 of 40 classes are evaluable.",
                "22 classes have only one device, so they cannot appear in the test set.",
                "Confusions are physical: coffee machine/iron → kettle; laptop/monitor → game console.",
            ],
            TEAL_DARK,
        ),
    ]
    for x, title, bullets, accent in cards:
        add_rect(slide, x, 1.72, 3.72, 4.15, LIGHT, BORDER, radius=0.06)
        add_text(slide, title, x + 0.20, 1.90, 3.32, 0.30, 11.5, accent, True)
        for index, bullet in enumerate(bullets):
            add_text(slide, "•  " + bullet, x + 0.20, 2.38 + index * 1.02, 3.30, 0.90, 9.3, BODY)
    add_callout(
        slide,
        "What would change the conclusion: focal/oversampling for microwave, a cross-dataset test, and a full 3-seed repeat.",
        4.55,
        6.10,
        7.82,
        0.72,
        fill=PALE_RED,
        color=RGBColor(0x99, 0x1B, 0x1B),
        size=10.5,
        bold=True,
    )
    add_footer(slide, 11)

    # 12 — Architecture
    slide = blank(prs)
    add_section(slide, "07", "System", "FIVE LAYERS")
    add_header(
        slide,
        "END TO END",
        "Five layers, one pipeline",
        "Every layer is in this repository and runs on one laptop.",
    )
    layers = [
        ("DATA", "Data", "UK-DALE  ·  WHITED  ·  replay adapter", "6.3 GB + 225 MB"),
        ("MODEL", "Model", "6 s windows  ·  Seq2Point  ·  ONNX Runtime", "10 exported models"),
        ("SERVICE", "Service", "FastAPI  ·  SQLite  ·  cache  ·  JWT", "38 API paths"),
        ("APPS", "Apps", "Vue 3 Web  ·  uni-app H5 (English)", "same REST API"),
        ("QUALITY", "Quality", "21 API checks  ·  generated OpenAPI  ·  scripts", "reproducible runs"),
    ]
    for index, (tag, title, detail, right) in enumerate(layers):
        y = 1.74 + index * 0.92
        add_rect(slide, 4.55, y, 0.92, 0.78, TEAL_DARK, radius=0.1)
        add_text(slide, tag, 4.55, y + 0.20, 0.92, 0.25, 8, WHITE, True, align=PP_ALIGN.CENTER, spacing=80)
        add_rect(slide, 5.55, y, 6.10, 0.78, LIGHT, BORDER, radius=0.1)
        add_text(slide, title, 5.72, y + 0.08, 1.35, 0.28, 11.5, NAVY, True)
        add_text(slide, detail, 7.05, y + 0.08, 3.6, 0.28, 9.2, BODY)
        add_text(slide, right, 10.55, y + 0.08, 1.0, 0.25, 8.2, MUTED, align=PP_ALIGN.RIGHT)
    add_callout(
        slide,
        "One command starts everything:  .\\scripts\\demo_web.ps1",
        4.55,
        6.38,
        8.10,
        0.55,
        fill=PALE_GREEN,
        color=TEAL_DARK,
        size=11,
        bold=True,
    )
    add_footer(slide, 10)

    # 11 — Web console
    slide = blank(prs)
    add_section(slide, "07", "System", "WEB CONSOLE")
    add_header(
        slide,
        "VUE 3  ·  ECHARTS",
        "The console shows it live",
        "Dashboard  ·  Evaluation  ·  Analytics",
    )
    add_rect(slide, 10.78, 1.40, 1.28, 0.28, ORANGE, radius=0.2)
    add_text(slide, "LIVE DEMO", 10.78, 1.44, 1.28, 0.20, 7.5, WHITE, True, align=PP_ALIGN.CENTER, spacing=60)
    add_figure(slide, SHOTS / "web_dashboard_tall.png", 4.55, 1.68, 7.55, 4.95, pad=0.04)
    add_text(
        slide,
        "Demo path: Login · Refresh · Evaluation · Analytics. Same API, live data.",
        4.57,
        6.68,
        8.0,
        0.3,
        8.8,
        MUTED,
    )
    add_footer(slide, 11)

    # 12 — Mobile
    slide = blank(prs)
    add_section(slide, "07", "System", "MOBILE H5")
    add_header(
        slide,
        "UNI-APP  ·  SAME API",
        "Same data, in your hand",
        "A second client, built once and shipped to H5 today.",
    )
    add_rect(slide, 4.72, 1.82, 2.58, 4.95, RGBColor(0x0F, 0x17, 0x2A), radius=0.12)
    add_rect(slide, 4.82, 1.92, 2.38, 4.75, WHITE, radius=0.08)
    add_picture_fit(slide, SHOTS / "mobile_analytics.png", 4.88, 2.20, 2.26, 4.35)
    add_rect(slide, 5.64, 2.00, 0.72, 0.10, RGBColor(0x0F, 0x17, 0x2A), radius=0.5)
    add_text(slide, "English-only UI", 7.70, 1.82, 4.8, 0.4, 20, TEAL_DARK, True)
    add_text(
        slide,
        "Every label, appliance name and alert is English.",
        7.72,
        2.28,
        4.8,
        0.3,
        10.5,
        MUTED,
    )
    bullets = [
        ("Monitor", "live power + F1 score"),
        ("Devices", "status, energy and threshold"),
        ("Analytics", "bill, unmetered energy and alerts"),
        ("Profile", "power limit and sign out"),
    ]
    for index, (title, detail) in enumerate(bullets):
        y = 2.90 + index * 0.72
        add_rect(slide, 7.72, y + 0.10, 0.10, 0.10, TEAL, radius=0.5, shape=MSO_SHAPE.OVAL)
        add_text(slide, title, 8.00, y, 1.25, 0.28, 11, NAVY, True)
        add_text(slide, detail, 9.15, y, 3.35, 0.28, 9.5, BODY)
    add_callout(
        slide,
        "H5 today  ·  WeChat mini-program and native builds next.",
        7.72,
        5.92,
        4.75,
        0.55,
        fill=PALE_GREEN,
        color=TEAL_DARK,
        size=10,
        bold=True,
    )
    add_footer(slide, 12)

    # 13 — Why accuracy is not proven
    slide = blank(prs)
    add_section(slide, "08", "Limits", "WHY NOT PROVEN?")
    add_header(
        slide,
        "WHAT WOULD COUNT AS PROOF?",
        "Why we can't claim accuracy yet",
        "One house, overlapping windows and rare events are not a proof of generalisation.",
    )
    reasons = [
        ("1", "One house", "UK-DALE house 1", "No cross-house test; the model can learn this building's quirks."),
        ("2", "Overlapping windows", "13,013 test windows", "3-minute stride: adjacent windows share most samples, so they are not independent."),
        ("3", "Rare events", "34 microwave positives", f"The confidence interval is wide; F1 {metric('microwave', 'attention', 'event_f1'):.2f} is not a stable estimate."),
    ]
    for index, (number, title, big, detail) in enumerate(reasons):
        x = 4.55 + index * 2.76
        add_rect(slide, x, 1.76, 2.58, 3.42, LIGHT, BORDER, radius=0.08)
        add_rect(slide, x + 0.18, 1.96, 0.36, 0.36, TEAL, radius=0.5, shape=MSO_SHAPE.OVAL)
        add_text(slide, number, x + 0.18, 2.01, 0.36, 0.22, 9, WHITE, True, align=PP_ALIGN.CENTER)
        add_text(slide, title, x + 0.66, 1.98, 1.80, 0.28, 12, NAVY, True)
        add_text(slide, big, x + 0.20, 2.55, 2.20, 0.65, 17, TEAL_DARK, True)
        add_text(slide, detail, x + 0.20, 3.30, 2.18, 1.15, 9.2, BODY)
        takeaway = ["So: no generalisation claim", "So: windows are not independent", "So: report per-class counts"][index]
        add_text(slide, takeaway, x + 0.20, 4.58, 2.18, 0.30, 8.3, TEAL_DARK, True)
    add_text(
        slide,
        "REAL NOW   ONNX · Web · mobile · 21 API checks        OPEN   cross-house · confidence intervals · WHITED CNN",
        4.57,
        5.38,
        8.05,
        0.28,
        8.4,
        MUTED,
    )
    add_callout(
        slide,
        "What would prove it: a cross-house test, event-level confidence intervals, and more than one building.",
        4.55,
        5.82,
        8.10,
        0.95,
        fill=PALE_RED,
        color=RGBColor(0x99, 0x1B, 0x1B),
        size=11,
        bold=True,
    )
    add_footer(slide, 13)

    # 14 — Next
    slide = blank(prs)
    add_section(slide, "09", "Next", "TWO-WEEK PLAN")
    add_header(
        slide,
        "PRIORITIES",
        "Next two weeks",
        "Four workstreams; one decision needed from you.",
    )
    plans = [
        ("1", "Model", "Focal loss + oversampling; fix microwave recall", "YangYifei", "Output: new F1 + curves"),
        ("2", "Evidence", "Truth-vs-pred + threshold + CI", "JinXinyi", "Output: proof pack"),
        ("3", "Data", "House 2 cross-house test", "JinXinyi", "Output: cross-house F1"),
        ("4", "Quality", "pytest + CI after 11.25", "YangYifei", "Output: green CI"),
    ]
    positions = [(4.55, 1.75), (7.75, 1.75), (4.55, 3.55), (7.75, 3.55)]
    for (number, title, detail, owner, output), (x, y) in zip(plans, positions):
        add_rect(slide, x, y, 3.00, 1.62, LIGHT, BORDER, radius=0.1)
        add_rect(slide, x + 0.18, y + 0.18, 0.34, 0.34, TEAL, radius=0.5, shape=MSO_SHAPE.OVAL)
        add_text(slide, number, x + 0.18, y + 0.23, 0.34, 0.20, 9, WHITE, True, align=PP_ALIGN.CENTER)
        add_text(slide, title, x + 0.66, y + 0.16, 1.8, 0.3, 13, NAVY, True)
        add_text(slide, detail, x + 0.20, y + 0.64, 2.6, 0.30, 9.5, BODY)
        add_text(slide, output, x + 0.20, y + 0.96, 2.6, 0.24, 8.3, TEAL_DARK)
        add_text(slide, owner, x + 0.20, y + 1.30, 2.6, 0.22, 8.2, MUTED)
    add_callout(
        slide,
        "Decision: approve ~2 h GPU time and house-2 preprocessing. 11.25 focus: evidence, not new features.",
        4.55,
        5.55,
        8.10,
        1.05,
        fill=PALE_GREEN,
        color=TEAL_DARK,
        size=11.5,
        bold=True,
    )
    add_footer(slide, 14)

    # 15 — Closing
    slide = blank(prs)
    add_rect(slide, 0.72, 0.72, 11.90, 6.05, TEAL, radius=0, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, "ONE METER. FIVE APPLIANCES.", 1.15, 1.45, 11.0, 0.35, 10, WHITE, True, spacing=140)
    add_text(slide, "Real data, honest results.", 1.15, 2.00, 11.0, 1.1, 40, WHITE, True)
    add_text(
        slide,
        "The system runs end to end. The next step is to make the model claim as strong as the software.",
        1.18,
        3.30,
        10.6,
        0.8,
        16,
        WHITE,
        line_spacing=1.1,
    )
    add_rect(slide, 1.18, 4.45, 2.2, 0.035, WHITE, radius=0, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, "Questions?", 1.15, 4.75, 5.0, 0.8, 30, WHITE, True)
    add_text(slide, "JinXinyi  ·  YangYifei  ·  YuShengbin", 1.18, 5.85, 8.0, 0.3, 11, WHITE)
    add_text(slide, "25 November 2026", 1.18, 6.15, 5.0, 0.3, 10, WHITE)

    notes = [
        "Welcome. This is the 25 November progress report. The system runs on real data; the model results are reported honestly.",
        "NILM means one meter at the main switch, plus software that separates the appliances. No sensor is installed on each device.",
        "We moved from a synthetic demo to a real pipeline: real data, trained models, ONNX export, and both clients running.",
        "UK-DALE house 1: six months, one reading every six seconds. The top panel is what the meter sees; the bottom panel is what is actually on.",
        "This is the class-imbalance slide. The microwave is ON only 0.39% of the time and has just 34 positive test windows. A model can look accurate by always saying OFF; that is why we use F1.",
        "All epochs are shown. Training loss keeps falling, but validation loss flattens after about epoch 6. The best checkpoint is chosen by validation event F1, not the last epoch.",
        "The baseline is a standard five-layer CNN. The attention model is smaller and adds channel and temporal attention. Same input, same output, same loss.",
        "These are test-set results. Four appliances are strong; microwave is weak. The baseline is still competitive, and we say so.",
        "Even at the best threshold, microwave recall is low. A 25× positive-weighted MSE raises Event F1 from 0.407 to 0.494 and recall to 0.68, with precision flat and slightly higher MAE; this is the targeted improvement experiment.",
        "A two-hour window. Navy is the measured total; colours are the model estimates. These are estimates, not ground truth.",
        "These are the professor's red circles. At 90-120 minutes the dishwasher is truly about 1.1 kW, but the model outputs about 0.1 kW. The residual is small, so this is a model recall failure, not an unmodeled appliance.",
        "WHITED is a second dataset: high-frequency start-up current from 100 devices. These short transients are another kind of appliance fingerprint.",
        "We test on devices the model has never seen. Only 18 of 40 classes have more than one device, so this is a baseline, not a final result.",
        "This is the full 40-class distribution. The long tail explains the 44.1% accuracy: 22 classes have only one device and therefore cannot be tested at all.",
        "This slide answers 'why are the numbers what they are'. UK-DALE: attention wins MAE and Event F1 but loses State F1 and the cross-house ranking flips. WHITED: only 18 of 40 classes are evaluable, and the confusions are physically similar loads.",
        "Five layers: data, model, service, apps, and quality. All of them live in the repository and run locally.",
        "This is the live Web console. The demo path is login, refresh, evaluation, analytics.",
        "This is the mobile H5 client. It is English-only and talks to the same backend.",
        "Why can't we claim accuracy yet? One house, overlapping windows, and rare events. A cross-house test and confidence intervals are what would count as proof.",
        "Next two weeks: fix microwave recall, build the evidence pack, run house 2, and defer tests and CI until after 11.25.",
        "Thank you. Questions?",
    ]
    for slide, note in zip(prs.slides, notes):
        slide.notes_slide.notes_text_frame.text = note

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"wrote {OUT} with {len(prs.slides)} slides")


if __name__ == "__main__":
    build()
