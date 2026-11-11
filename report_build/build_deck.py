"""Build the bi-weekly NILM progress deck in the style of NILM-pre10.21.pptx."""

from __future__ import annotations

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
OUT = ROOT / "NILM-pre11.11.pptx"

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


def rgb(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value)


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


def add_footer(slide, page):
    add_text(
        slide,
        f"NILM progress report  ·  11 Nov 2026  ·  {page:02d}",
        8.4,
        7.12,
        4.4,
        0.22,
        8,
        MUTED,
        align=PP_ALIGN.RIGHT,
    )


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

    # 1 — Title
    slide = blank(prs)
    add_rect(slide, 0, 0.72, 8.45, 6.05, TEAL, radius=0, shape=MSO_SHAPE.RECTANGLE)
    add_rect(slide, 8.95, 0.72, 3.85, 6.05, GREY_BG, radius=0, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, "BI-WEEKLY REPORT  ·  11 NOV 2026", 0.78, 1.18, 6.8, 0.3, 10, WHITE, True, spacing=120)
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

    # 5 — Model
    slide = blank(prs)
    add_section(slide, "04", "Model", "HOW IT LEARNS")
    add_header(
        slide,
        "SEQ2POINT  ·  ONE MODEL PER APPLIANCE",
        "How the model learns",
        "599 readings in; one appliance power value out.",
    )
    pipeline = [
        ("599 samples", "one hour"),
        ("1-D CNN", "+ attention"),
        ("Appliance watts", "one value"),
        ("ON/OFF + kWh", "what users see"),
    ]
    for index, (top, bottom) in enumerate(pipeline):
        x = 4.55 + index * 2.03
        add_rect(slide, x, 1.78, 1.72, 0.66, LIGHT, BORDER, radius=0.12)
        add_text(slide, top, x + 0.12, 1.83, 1.48, 0.24, 9.8, NAVY, True, align=PP_ALIGN.CENTER)
        add_text(slide, bottom, x + 0.12, 2.07, 1.48, 0.22, 8.2, MUTED, align=PP_ALIGN.CENTER)
        if index < 3:
            add_rect(slide, x + 1.76, 2.03, 0.22, 0.16, BORDER, radius=0.2, shape=MSO_SHAPE.RIGHT_ARROW)
    add_figure(slide, FIGS / "fig_training.png", 4.55, 2.72, 7.55, 2.85)
    add_text(
        slide,
        "3 epochs  ·  60,797 training windows per appliance  ·  RTX 3070",
        4.55,
        5.68,
        7.6,
        0.25,
        9,
        MUTED,
    )
    add_callout(
        slide,
        "The same 1-hour window feeds five separate models; each one specialises in a single appliance.",
        4.55,
        6.05,
        8.10,
        0.72,
        size=11.5,
    )
    add_footer(slide, 5)

    # 6 — Results
    slide = blank(prs)
    add_section(slide, "05", "Results", "DOES IT WORK?")
    add_header(
        slide,
        "TEST SET  ·  13,013 WINDOWS PER APPLIANCE",
        "Good on four. Weak on one.",
        "Event F1 = how often ON/OFF events are correct. Average 0.71; the baseline CNN is 0.76.",
    )
    add_figure(slide, FIGS / "fig_metrics.png", 4.55, 1.72, 8.08, 3.95)
    for index, (number, label) in enumerate(
        [("0.71", "average event F1"), ("0.68", "average state F1"), ("11.4 W", "average MAE")]
    ):
        add_stat(slide, number, label, 4.55 + index * 2.70, 5.85, 2.55, 0.72, number_size=19)
    add_text(
        slide,
        "Attention wins on dishwasher and washing machine; baseline still wins on fridge, kettle and microwave.",
        4.55,
        6.66,
        8.1,
        0.3,
        8.5,
        MUTED,
    )
    add_footer(slide, 6)

    # 7 — Disaggregation example
    slide = blank(prs)
    add_section(slide, "05", "Results", "ONE WINDOW")
    add_header(
        slide,
        "TWO-HOUR EXAMPLE",
        "One signal in. Five signals out.",
        "Measured mains (navy) versus model estimates (colours).",
    )
    add_figure(slide, FIGS / "fig_disagg.png", 4.55, 1.72, 8.08, 3.95)
    add_callout(
        slide,
        "The kettle and dishwasher events are recovered from the total; fridge cycles remain visible as a low baseline.",
        4.55,
        5.85,
        8.10,
        0.82,
        size=11.5,
    )
    add_footer(slide, 7)

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

    # 10 — Architecture
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
    add_figure(slide, SHOTS / "web_dashboard_tall.png", 4.55, 1.68, 7.55, 4.95, pad=0.04)
    add_text(
        slide,
        "Live mains and five appliance cards.  Model F1, energy and alerts update from the same API.",
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

    # 13 — Status
    slide = blank(prs)
    add_section(slide, "08", "Status", "HONEST VIEW")
    add_header(
        slide,
        "WHAT IS PROVEN?",
        "Real vs still open",
        "We separate working software from unsettled model claims.",
    )
    columns = [
        (
            "REAL NOW",
            GREEN,
            PALE_GREEN,
            [
                "UK-DALE + WHITED data",
                "ONNX inference, 5 appliances",
                "Real test-set metrics",
                "Web + mobile H5",
                "21 API checks pass",
            ],
        ),
        (
            "BASELINE",
            AMBER,
            RGBColor(0xFF, 0xF8, 0xE6),
            [
                "WHITED 44.1% accuracy",
                "Attention 0.71 vs baseline 0.76",
                "Only one house evaluated",
                "Microwave F1 only 0.29",
            ],
        ),
        (
            "OPEN",
            MUTED,
            RGBColor(0xF4, 0xF6, 0xF8),
            [
                "Cross-house generalisation",
                "Unit tests and CI",
                "Database migrations",
                "Raw-waveform WHITED CNN",
            ],
        ),
    ]
    for index, (title, accent, fill, items) in enumerate(columns):
        x = 4.55 + index * 2.76
        add_rect(slide, x, 1.78, 2.58, 0.50, accent, radius=0.1)
        add_text(slide, title, x, 1.88, 2.58, 0.25, 9, WHITE, True, align=PP_ALIGN.CENTER, spacing=100)
        add_rect(slide, x, 2.38, 2.58, 3.55, fill, BORDER, radius=0.04)
        for item_index, item in enumerate(items):
            add_text(slide, "•  " + item, x + 0.18, 2.58 + item_index * 0.60, 2.25, 0.50, 9.5, BODY)
    add_callout(
        slide,
        "The system is real. The model claim is not settled yet - and this report says so.",
        4.55,
        6.15,
        8.10,
        0.68,
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
        ("1", "Model", "Fair attention vs baseline; fix microwave", "YangYifei", "Output: updated ablation table"),
        ("2", "Data", "House 2 cross-house test", "JinXinyi", "Output: cross-house F1"),
        ("3", "Quality", "pytest + CI + database migrations", "JinXinyi", "Output: green CI + migrations"),
        ("4", "WHITED", "Raw-waveform 1-D CNN", "YangYifei", "Output: CNN vs 44.1% baseline"),
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
        "Decision: approve ~2 h GPU time and house-2 preprocessing. Then we can report cross-house numbers next time.",
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
    add_text(slide, "11 November 2026", 1.18, 6.15, 5.0, 0.3, 10, WHITE)

    notes = [
        "Welcome. This is a two-week progress report. The key message: the system now runs on real data, and we report the model results honestly.",
        "NILM means one meter at the main switch, plus software that separates the appliances. No sensor is installed on each device.",
        "In two weeks we moved from a synthetic demo to a real pipeline: real data, trained models, ONNX export, and both clients running.",
        "UK-DALE house 1: six months, one reading every six seconds. The top panel is what the meter sees; the bottom panel is what is actually on.",
        "The model sees a one-hour window of 599 readings and predicts one appliance's power at the centre. We train one model per appliance.",
        "Event F1 measures how often switch-on/off events are correct. Four appliances are strong; microwave is weak. The baseline is still slightly better on average.",
        "A two-hour example. Navy is the measured total; colours are the model's estimates. Kettle and dishwasher events are recovered from the total.",
        "WHITED is a second dataset: high-frequency start-up current from 100 devices. These short transients are another kind of appliance fingerprint.",
        "We test on devices the model has never seen, which is strict. Only 18 of 40 classes have more than one device, so this is a baseline, not a final result.",
        "Five layers: data, model, service, apps, and quality. All of them live in the repository and run locally.",
        "This is the live Web console. The same API feeds the dashboard, evaluation and analytics pages.",
        "This is the mobile H5 client. It is English-only and talks to the same backend.",
        "We separate what is proven from what is still open. The software is real; the model claim is not settled yet.",
        "Next two weeks: fair model comparison, cross-house data, tests and migrations, and a WHITED CNN. We need GPU time and house-2 preprocessing.",
        "Thank you. Questions?",
    ]
    for slide, note in zip(prs.slides, notes):
        slide.notes_slide.notes_text_frame.text = note

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"wrote {OUT} with {len(prs.slides)} slides")


if __name__ == "__main__":
    build()
