from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计")
OUT = ROOT / "NILM" / "MIDTERM_PLAN_2026-11-19.xlsx"

FONT = "Corbel"
TEAL_DARK = "16606B"
TEAL = "40BAD2"
LIGHT = "EAF7FA"
PALE = "F7FBFC"
ORANGE = "EE7008"
AMBER = "FAB900"
GREEN = "1AB39F"
LIME = "90BB23"
PURPLE = "7C5CBF"
RED = "D5393D"
GREY = "64748B"
BORDER = "D7E3E8"
WHITE = "FFFFFF"

THIN = Side(style="thin", color=BORDER)
CELL_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def font(size=11, bold=False, color="14333D", italic=False) -> Font:
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)


def title_block(ws, title: str, subtitle: str, last_col: int) -> None:
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    cell = ws.cell(row=1, column=1, value=title)
    cell.fill = fill(TEAL_DARK)
    cell.font = font(20, True, WHITE)
    cell.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    ws.row_dimensions[1].height = 36

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    cell = ws.cell(row=2, column=1, value=subtitle)
    cell.fill = fill(LIGHT)
    cell.font = font(10, False, TEAL_DARK)
    cell.alignment = Alignment(vertical="center", horizontal="left", indent=1, wrap_text=True)
    ws.row_dimensions[2].height = 30


def header_row(ws, row: int, headers: list[str], height=30) -> None:
    for col, value in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=value)
        cell.fill = fill(TEAL_DARK)
        cell.font = font(10.5, True, WHITE)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = CELL_BORDER
    ws.row_dimensions[row].height = height


def body_row(ws, row: int, values: list, *, height=34, wrap=True, banded=False) -> None:
    for col, value in enumerate(values, 1):
        cell = ws.cell(row=row, column=col, value=value)
        cell.font = font(10, False, "14333D")
        cell.alignment = Alignment(vertical="top", wrap_text=wrap)
        cell.border = CELL_BORDER
        if banded:
            cell.fill = fill(PALE)
    ws.row_dimensions[row].height = height


def widths(ws, mapping: dict[str, int]) -> None:
    for col, width in mapping.items():
        ws.column_dimensions[col].width = width


def add_status_validation(ws, status_col: str, first_row: int, last_row: int) -> None:
    dv = DataValidation(
        type="list",
        formula1='"Done,In progress,Planned,Blocked"',
        allow_blank=True,
        showDropDown=False,
    )
    ws.add_data_validation(dv)
    dv.add(f"{status_col}{first_row}:{status_col}{last_row}")


def status_format(ws, status_col: str, first_row: int, last_row: int) -> None:
    rng = f"{status_col}{first_row}:{status_col}{last_row}"
    ws.conditional_formatting.add(
        rng, FormulaRule(formula=[f'${status_col}{first_row}="Done"'], fill=fill("D9F2EA"))
    )
    ws.conditional_formatting.add(
        rng, FormulaRule(formula=[f'${status_col}{first_row}="In progress"'], fill=fill("FFF1D6"))
    )
    ws.conditional_formatting.add(
        rng, FormulaRule(formula=[f'${status_col}{first_row}="Blocked"'], fill=fill("FADBD8"))
    )


def setup_print(ws, last_col: int, last_row: int) -> None:
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_area = f"A1:{get_column_letter(last_col)}{last_row}"
    ws.sheet_view.showGridLines = False


def sheet_readme(wb: Workbook) -> None:
    ws = wb.active
    ws.title = "ReadMe"
    title_block(
        ws,
        "FYP Midterm & Biweekly Plan",
        "Building-Level NILM System  ·  plan v1.0  ·  generated 2026-11-19  ·  source: FYP042Proposal.docx + Lecture 4 Midterm report.pptx + BIT Progress Report Template",
        6,
    )
    widths(ws, {"A": 26, "B": 70, "C": 22, "D": 24, "E": 20, "F": 20})

    rows = [
        ("Key deadline", "2026-11-30 (Mon): submit the Progress Report via WEMUST questionnaire."),
        ("Key deadline", "2026-12-07 (Mon): oral report, 10 minutes presentation + 5 minutes Q&A."),
        ("Midterm weight", "15 points: PO(d) Design & Implementation 10 + PO(g) Communication 5."),
        ("Report length", "Suggested 8 chapters, §1 1p, §2 1p, §3 2-3p, §4 2-3p, §5 1-2p, §6 1p, §7 0.5p, §8 remainder."),
        ("Submission format", "BIT cover + abstract + contributions, then the 8-chapter body recommended by Lecture 4."),
        ("Evidence rule", "Every number must point to a commit/tag + test script + LogBook week; report adverse results, no cherry-picking."),
        ("Biweekly cadence", "Every second Wednesday; 11/25 is the pre-midterm checkpoint. 12/09, 12/23, 01/06, 01/20 ..."),
        ("Weekly LogBook", "Every Friday: last week plan / this week implementation / next week plan; 25 points, separate from the report."),
        ("Final deadline", "Final report/defense date is not in the supplied files; Apr-May 2027 is reserved as TBD and must be updated when announced."),
        ("Team name check", "Proposal says U SENGPAN; the 11/25 deck says YuShengbin. Confirm the official English/Chinese name before submission."),
    ]
    r = 4
    for label, value in rows:
        ws.cell(row=r, column=1, value=label).font = font(10.5, True, TEAL_DARK)
        ws.cell(row=r, column=1).fill = fill(LIGHT)
        ws.cell(row=r, column=1).border = CELL_BORDER
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        c = ws.cell(row=r, column=2, value=value)
        c.font = font(10, False, "14333D")
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = CELL_BORDER
        ws.row_dimensions[r].height = 36
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="How to use this workbook").font = font(13, True, TEAL_DARK)
    r += 1
    guide = [
        ("Gantt", "One-page timeline; coloured bars show the critical path."),
        ("Master Plan", "Task-level plan with owner, proposal reference, acceptance and evidence."),
        ("Report Calendar", "All biweekly meetings, 11/30 submission, 12/07 oral and thesis milestones."),
        ("Nov30 Report", "Chapter-by-chapter checklist for the 8-chapter midterm report."),
        ("Proposal Gaps", "O1-O7 commitments vs current state, with the exact closure action."),
        ("Biweekly Log", "Fill this before each professor meeting; one row per meeting."),
    ]
    for name, desc in guide:
        ws.cell(row=r, column=1, value=name).font = font(10.5, True, TEAL_DARK)
        ws.cell(row=r, column=1).fill = fill(LIGHT)
        ws.cell(row=r, column=1).border = CELL_BORDER
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        c = ws.cell(row=r, column=2, value=desc)
        c.font = font(10, False, "14333D")
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = CELL_BORDER
        ws.row_dimensions[r].height = 30
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="Assumptions / decisions to confirm").font = font(13, True, TEAL_DARK)
    r += 1
    assumptions = [
        "The 8-chapter Lecture 4 structure is used for the body; the BIT template supplies the cover, abstract and contributions. Confirm with the TA.",
        "11/25 is assumed to be the next biweekly meeting (11/11 + two weeks). Dates after 12/07 are working targets and can move with the school calendar.",
        "The midterm report will honestly state which proposal items are not yet validated: REDD/PLAID, house 2, dilated-only, loss ablation, Redis, Modbus/MQTT.",
        "Any scope change must have four elements: original commitment, new commitment, reason/impact, advisor confirmation + planned week.",
    ]
    for text in assumptions:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
        c = ws.cell(row=r, column=1, value="• " + text)
        c.font = font(10, False, "14333D")
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.row_dimensions[r].height = 34
        r += 1

    setup_print(ws, 6, r)


def sheet_gantt(wb: Workbook) -> None:
    ws = wb.create_sheet("Gantt")
    start = date(2026, 11, 16)
    end = date(2027, 5, 31)
    weeks = []
    d = start
    while d <= end:
        weeks.append(d)
        d += timedelta(days=7)
    last_col = 4 + len(weeks)
    title_block(
        ws,
        "Gantt  ·  Nov 2026 → May 2027",
        "Critical path: midterm report → oral → research gaps → system hardening → final experiments → thesis. Final dates marked TBD.",
        last_col,
    )
    widths(ws, {"A": 34, "B": 15, "C": 11, "D": 11})
    for idx in range(5, last_col + 1):
        ws.column_dimensions[get_column_letter(idx)].width = 3.4

    # Month band
    month_row = 3
    ws.cell(row=month_row, column=1, value="Task").font = font(9, True, WHITE)
    ws.cell(row=month_row, column=1).fill = fill(TEAL_DARK)
    ws.merge_cells(start_row=month_row, start_column=1, end_row=month_row, end_column=2)
    ws.cell(row=month_row, column=3, value="Start").font = font(9, True, WHITE)
    ws.cell(row=month_row, column=3).fill = fill(TEAL_DARK)
    ws.cell(row=month_row, column=4, value="End").font = font(9, True, WHITE)
    ws.cell(row=month_row, column=4).fill = fill(TEAL_DARK)
    for idx, week in enumerate(weeks, 5):
        ws.cell(row=month_row, column=idx, value=week.strftime("%b")).font = font(8, True, TEAL_DARK)
        ws.cell(row=month_row, column=idx).fill = fill(LIGHT)
        ws.cell(row=month_row, column=idx).alignment = Alignment(horizontal="center")
    # Merge month labels roughly by first-of-month occurrence
    group_start = 5
    current_month = weeks[0].strftime("%b")
    for idx, week in enumerate(weeks[1:], 6):
        month = week.strftime("%b")
        if month != current_month:
            if idx - 1 > group_start:
                ws.merge_cells(start_row=month_row, start_column=group_start, end_row=month_row, end_column=idx - 1)
                ws.cell(row=month_row, column=group_start, value=current_month)
                ws.cell(row=month_row, column=group_start).alignment = Alignment(horizontal="center")
            group_start = idx
            current_month = month
    if last_col >= group_start:
        ws.merge_cells(start_row=month_row, start_column=group_start, end_row=month_row, end_column=last_col)
        ws.cell(row=month_row, column=group_start, value=current_month)
        ws.cell(row=month_row, column=group_start).alignment = Alignment(horizontal="center")
    ws.row_dimensions[month_row].height = 18

    header_row(ws, 4, ["Task", "Owner", "Start", "End"] + [w.strftime("%m/%d") for w in weeks], height=44)
    for col in range(5, last_col + 1):
        ws.cell(row=4, column=col).alignment = Alignment(text_rotation=90, horizontal="center", vertical="bottom")

    tasks = [
        ("Midterm report + evidence", "Jin/Yang", date(2026, 11, 16), date(2026, 11, 30), ORANGE, "P0"),
        ("Model ablations, RMSE, 3 seeds", "Yang", date(2026, 11, 20), date(2026, 11, 28), ORANGE, "P0"),
        ("House 2 / cross-house attempt", "Jin", date(2026, 11, 22), date(2026, 12, 22), TEAL, "P1"),
        ("REDD/PLAID + robustness", "Yang", date(2026, 12, 8), date(2027, 1, 15), TEAL, "P1"),
        ("System hardening (tests/CI/Redis/Modbus)", "Jin", date(2026, 12, 24), date(2027, 1, 15), GREEN, "P2"),
        ("WHITED CNN + quantization", "Yang", date(2027, 1, 16), date(2027, 2, 15), LIME, "P3"),
        ("Final experiments + results freeze", "Yang/Jin", date(2027, 2, 1), date(2027, 2, 28), LIME, "P3"),
        ("Thesis draft + figures", "All", date(2027, 3, 1), date(2027, 3, 31), PURPLE, "P4"),
        ("Final report + defense", "All", date(2027, 4, 1), date(2027, 5, 15), RED, "P5"),
    ]
    row = 5
    for name, owner, s, e, color, phase in tasks:
        body_row(ws, row, [name, owner, s, e], height=24, wrap=False)
        ws.cell(row=row, column=3).number_format = "yyyy-mm-dd"
        ws.cell(row=row, column=4).number_format = "yyyy-mm-dd"
        for idx, week in enumerate(weeks, 5):
            cell = ws.cell(row=row, column=idx)
            cell.fill = fill(color if s <= week <= e else WHITE)
            cell.border = Border(left=Side(style="hair", color="EEF2F5"), right=Side(style="hair", color="EEF2F5"), top=Side(style="hair", color="EEF2F5"), bottom=Side(style="hair", color="EEF2F5"))
        row += 1

    # Milestones
    milestones = [
        ("11/25 biweekly", date(2026, 11, 25), AMBER),
        ("11/30 report due", date(2026, 11, 30), RED),
        ("12/07 oral", date(2026, 12, 7), RED),
    ]
    row += 1
    ws.cell(row=row, column=1, value="Milestones").font = font(11, True, TEAL_DARK)
    row += 1
    for name, mdate, color in milestones:
        body_row(ws, row, [name, "", mdate, ""], height=22, wrap=False)
        for idx, week in enumerate(weeks, 5):
            if week <= mdate <= week + timedelta(days=6):
                ws.cell(row=row, column=idx).fill = fill(color)
        ws.cell(row=row, column=3).number_format = "yyyy-mm-dd"
        row += 1

    # Legend
    row += 1
    ws.cell(row=row, column=1, value="Legend").font = font(11, True, TEAL_DARK)
    row += 1
    legend = [("P0 midterm sprint", ORANGE), ("P1 research evidence", TEAL), ("P2 system hardening", GREEN), ("P3 final experiments", LIME), ("P4 thesis writing", PURPLE), ("P5 final/defense", RED)]
    for label, color in legend:
        cell = ws.cell(row=row, column=1)
        cell.fill = fill(color)
        cell.border = CELL_BORDER
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
        c = ws.cell(row=row, column=2, value=label)
        c.font = font(9, False, GREY)
        c.alignment = Alignment(vertical="center")
        row += 1

    setup_print(ws, last_col, row)


def sheet_master(wb: Workbook) -> None:
    ws = wb.create_sheet("Master Plan")
    title_block(
        ws,
        "Master Plan  ·  task-level",
        "Every row has an owner, proposal reference, acceptance condition and evidence. Status: Done / In progress / Planned / Blocked.",
        11,
    )
    widths(ws, {"A": 15, "B": 12, "C": 12, "D": 17, "E": 44, "F": 12, "G": 44, "H": 12, "I": 13, "J": 22, "K": 18})
    header_row(ws, 4, ["Phase", "Start", "End", "Workstream", "Task", "Proposal ref", "Deliverable / acceptance", "Owner", "Status", "Evidence / commit", "Report milestone"])

    rows = [
        ("P0", date(2026, 11, 19), date(2026, 11, 20), "Scope", "Freeze midterm scope; build O1-O7 commitment table; assign evidence owners", "O1-O7", "Scope table + owner map; no scope creep after 11/21", "Jin", "In progress", "README + SYSTEM_REVIEW", "11/25 deck"),
        ("P0", date(2026, 11, 20), date(2026, 11, 22), "Model", "Train dilated-only; MSE vs weighted-Huber; 3 seeds; RMSE + bootstrap CI", "O3/O4/O5", "ablation_metrics_v2.json + figures + tag; at least 3 seeds", "Yang", "Planned", "commit TBD", "§5 report"),
        ("P0", date(2026, 11, 22), date(2026, 11, 24), "Data", "House 2 download/preprocess + cross-house eval; fallback REDD if blocked", "O1/O5", "Cross-house table or a dated deviation note", "Jin", "Planned", "commit TBD", "§5 report"),
        ("P0", date(2026, 11, 24), date(2026, 11, 24), "Report", "Prepare 11/25 biweekly: evidence, gaps, scope confirmation", "—", "Deck v1 + one-page decision list", "All", "Planned", "NILM-pre11.25.pptx", "11/25"),
        ("P0", date(2026, 11, 25), date(2026, 11, 25), "Report", "11/25 professor meeting: confirm scope changes and evidence plan", "—", "Meeting notes with decisions", "All", "Planned", "Notes", "11/25"),
        ("P0", date(2026, 11, 25), date(2026, 11, 27), "Report", "Write §1-§5 (baseline, changes, design, implementation, validation)", "—", "Draft v0.8 with pages/figures", "Jin", "Planned", "commit TBD", "11/30"),
        ("P0", date(2026, 11, 28), date(2026, 11, 28), "Report", "Write §6-§8, Gantt, contributions, internal review", "—", "Draft v0.9; consistency chain §1→§2→§4→§6", "All", "Planned", "commit TBD", "11/30"),
        ("P0", date(2026, 11, 29), date(2026, 11, 29), "Report", "QA: commits, numbers, page limits, references, WEMUST upload", "—", "Final PDF + receipt", "Jin", "Planned", "tag midterm-2026-11-30", "11/30"),
        ("P0", date(2026, 11, 30), date(2026, 11, 30), "Milestone", "Submit Progress Report via WEMUST", "—", "Submission receipt", "Jin", "Planned", "WEMUST", "11/30"),
        ("P0", date(2026, 12, 1), date(2026, 12, 6), "Oral", "Build 10-min deck + 5-min Q&A; demo rehearsal", "—", "Oral deck + live demo + Q&A sheet", "All", "Planned", "Deck v1", "12/07"),
        ("P0", date(2026, 12, 7), date(2026, 12, 7), "Milestone", "Midterm oral report", "—", "15 points (PO(d) 10 + PO(g) 5)", "All", "Planned", "—", "12/07"),
        ("P1", date(2026, 12, 8), date(2026, 12, 22), "Research", "Cross-dataset (REDD or PLAID) + noise/missing/sampling robustness + WHITED CNN", "O1/O5", "Two generalization tables + failure analysis", "Yang", "Planned", "commit TBD", "12/23"),
        ("P1", date(2026, 12, 23), date(2026, 12, 23), "Report", "Post-oral biweekly: generalization results + final gap plan", "—", "Deck + decision list", "All", "Planned", "—", "12/23"),
        ("P2", date(2026, 12, 24), date(2027, 1, 15), "Engineering", "Redis/Postgres decision; Modbus/MQTT; self-contained Docker; pytest/CI/Alembic/RBAC", "O6/O7", "One working compose + CI green + test report", "Jin", "Planned", "commit TBD", "01/06"),
        ("P1", date(2027, 1, 6), date(2027, 1, 6), "Report", "Biweekly: system hardening status + remaining research gaps", "—", "Deck", "All", "Planned", "—", "01/06"),
        ("P3", date(2027, 1, 16), date(2027, 2, 15), "Research", "Final 3-model/loss ablation, 3-seed CI, quantization, latency/memory/size, model registry", "O3/O4/O5/O6", "Final tables with mean ± SD and commit", "Yang", "Planned", "commit TBD", "02/03"),
        ("P3", date(2027, 2, 1), date(2027, 2, 28), "Research", "Results freeze: cross-house + cross-dataset + robustness", "O1/O5", "Frozen results JSON + figures", "Yang/Jin", "Planned", "tag results-freeze", "02/17"),
        ("P4", date(2027, 2, 16), date(2027, 2, 28), "Thesis", "Results chapter, figures, Gantt, limitations", "—", "Chapter draft + 6 final figures", "All", "Planned", "commit TBD", "02/17"),
        ("P4", date(2027, 3, 1), date(2027, 3, 31), "Thesis", "Full thesis draft; internal review; references; formatting", "—", "Draft v1 + reviewer comments", "All", "Planned", "commit TBD", "03/17"),
        ("P5", date(2027, 4, 1), date(2027, 4, 30), "Final", "Final report + defense deck + demo; final QA", "—", "Submitted report + slides", "All", "Planned", "tag final", "04/28"),
        ("P5", date(2027, 5, 1), date(2027, 5, 31), "Buffer", "Defense rehearsal / buffer (official date TBD)", "—", "Final defense", "All", "Planned", "—", "05/12"),
    ]
    r = 5
    for idx, row_data in enumerate(rows):
        body_row(ws, r, list(row_data), height=44, banded=(idx % 2 == 1))
        for col in (2, 3):
            ws.cell(row=r, column=col).number_format = "yyyy-mm-dd"
            ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="top")
        r += 1

    add_status_validation(ws, "I", 5, r - 1)
    status_format(ws, "I", 5, r - 1)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:K{r - 1}"
    setup_print(ws, 11, r - 1)


def sheet_calendar(wb: Workbook) -> None:
    ws = wb.create_sheet("Report Calendar")
    title_block(
        ws,
        "Report & meeting calendar",
        "Weekly LogBook every Friday; biweekly professor meeting every second Wednesday; midterm report 11/30 and oral 12/07.",
        7,
    )
    widths(ws, {"A": 13, "B": 10, "C": 18, "D": 24, "E": 58, "F": 15, "G": 12})
    header_row(ws, 4, ["Date", "Day", "Type", "Audience / format", "Content focus", "Owner", "Status"])

    rows = [
        (date(2026, 11, 20), "Fri", "LogBook", "Weekly record", "Last week plan / this week implementation / next week plan", "All", "Planned"),
        (date(2026, 11, 25), "Wed", "Biweekly", "Professor meeting", "Pre-midterm checkpoint: ablation evidence, house-2 status, report skeleton, scope decisions", "All", "Planned"),
        (date(2026, 11, 27), "Fri", "LogBook", "Weekly record", "Midterm writing week; blockers", "Jin", "Planned"),
        (date(2026, 11, 30), "Mon", "FORMAL", "WEMUST questionnaire", "Submit Progress Report: 8 chapters, 15 points", "Jin", "Planned"),
        (date(2026, 12, 4), "Fri", "LogBook", "Weekly record", "Oral prep / demo rehearsal", "All", "Planned"),
        (date(2026, 12, 7), "Mon", "FORMAL", "Faculty team", "Oral report: 10 min + 5 min Q&A", "All", "Planned"),
        (date(2026, 12, 9), "Wed", "Biweekly", "Professor meeting", "Post-oral retro; final gap plan; cross-dataset decision", "All", "Planned"),
        (date(2026, 12, 23), "Wed", "Biweekly", "Professor meeting", "Generalization results; system hardening start", "All", "Planned"),
        (date(2027, 1, 6), "Wed", "Biweekly", "Professor meeting", "Backend/tests/Redis/Modbus status; thesis outline", "All", "Planned"),
        (date(2027, 1, 20), "Wed", "Biweekly", "Professor meeting", "Final ablation + quantization; results freeze plan", "All", "Planned"),
        (date(2027, 2, 3), "Wed", "Biweekly", "Professor meeting", "Cross-dataset/robustness results; thesis results chapter", "All", "Planned"),
        (date(2027, 2, 17), "Wed", "Biweekly", "Professor meeting", "Results chapter review; figures; risks", "All", "Planned"),
        (date(2027, 3, 3), "Wed", "Biweekly", "Professor meeting", "Full draft v1; remaining experiments", "All", "Planned"),
        (date(2027, 3, 17), "Wed", "Biweekly", "Professor meeting", "Draft review; final figure list", "All", "Planned"),
        (date(2027, 3, 31), "Wed", "Biweekly", "Professor meeting", "Thesis complete draft", "All", "Planned"),
        (date(2027, 4, 14), "Wed", "Biweekly", "Professor meeting", "Final report draft; defense story", "All", "Planned"),
        (date(2027, 4, 28), "Wed", "Biweekly", "Professor meeting", "Defense rehearsal; Q&A", "All", "Planned"),
        (date(2027, 5, 12), "Wed", "Buffer", "Professor meeting", "Buffer / official final date TBD", "All", "Planned"),
    ]
    r = 5
    for idx, row_data in enumerate(rows):
        body_row(ws, r, list(row_data), height=34, banded=(idx % 2 == 1))
        ws.cell(row=r, column=1).number_format = "yyyy-mm-dd"
        ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="top")
        # Highlight FORMAL rows
        if row_data[2] == "FORMAL":
            for col in range(1, 8):
                ws.cell(row=r, column=col).fill = fill("FDECEC")
        r += 1

    add_status_validation(ws, "G", 5, r - 1)
    status_format(ws, "G", 5, r - 1)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:G{r - 1}"
    setup_print(ws, 7, r - 1)


def sheet_nov30(wb: Workbook) -> None:
    ws = wb.create_sheet("Nov30 Report")
    title_block(
        ws,
        "Progress Report  ·  2026-11-30",
        "Lecture 4 recommends 8 chapters; BIT template supplies cover/abstract/contributions. Confirm the hybrid with the TA.",
        7,
    )
    widths(ws, {"A": 24, "B": 9, "C": 66, "D": 26, "E": 12, "F": 12, "G": 13})
    header_row(ws, 4, ["Section", "Pages", "Required content / what the rater looks for", "Evidence to attach", "Owner", "Draft due", "Status"])

    rows = [
        ("Cover + Abstract + Contributions", "1.5", "Title, team, date, version; 150-250 word abstract; per-member independent contribution (BIT template).", "Team names confirmed; version v1.0", "Jin", "11/26", "In progress"),
        ("§1 Baseline comparison", "1", "11/1 commitments vs 11/30 actual, O1-O7 one table; bad news first; every row has status and evidence.", "Commit/tag, metrics JSON, LogBook week", "Jin", "11/26", "In progress"),
        ("§2 Changes and scope", "1", "NILMTK→custom reader; 4→2 datasets; SQLite vs Redis/Postgres; Modbus/MQTT deferral; dilated-only/loss ablation deferral. Four elements: original → changed → reason/impact → advisor confirmation + week.", "11/25 meeting notes; advisor confirmation", "Jin", "11/26", "Planned"),
        ("§3 System design & architecture", "2-3", "4-layer architecture; M1-M5 modules, interfaces, owners, status; data flow; ONNX/FastAPI/Web/mobile; one architecture figure.", "Architecture figure; repo tree; API path list", "Jin/Yu", "11/27", "In progress"),
        ("§4 Implementation progress", "2-3", "Module × state × commit/tag table; completed / partially / future; unfinished table with reason and planned week; consistency statement linking §5 numbers to commits.", "git tag, commit list, test scripts", "Yang", "11/27", "Planned"),
        ("§5 Preliminary validation", "1-2", "Protocol; 13,013 test windows; metrics definitions; commitment vs actual table; 3 seeds mean±SD; adverse results (microwave 0.416, no cross-house, red-circle miss); failed attempts and why.", "ablation_metrics_v2.json, figures, commit", "Yang", "11/27", "Planned"),
        ("§6 Risks and next stage", "1", "W5-W8 milestones with deliverable + acceptance condition; risk table (data, model, system, report); every unfinished item has a week.", "Gantt; risk table", "Jin", "11/28", "Planned"),
        ("§7 Team division", "0.5", "Member × responsibility × output × main commit; objective, not adjectives.", "git shortlog; task board", "All", "11/28", "Planned"),
        ("§8 References & Appendix", "rest", "References; repo tag; API docs; test commands; AI-use disclosure; evidence index.", "Appendix A-F", "Jin", "11/28", "Planned"),
        ("Gantt + hardware/software", "1", "Update BIT Gantt with done/planned; update hardware/software list to actual (GPU, 6.3 GB data, Vue/ECharts, no Streamlit).", "Gantt figure; environment file", "Jin", "11/28", "Planned"),
    ]
    r = 5
    for idx, row_data in enumerate(rows):
        body_row(ws, r, list(row_data), height=66, banded=(idx % 2 == 1))
        r += 1

    add_status_validation(ws, "G", 5, r - 1)
    status_format(ws, "G", 5, r - 1)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:G{r - 1}"

    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    c = ws.cell(row=r, column=1, value="Consistency chain: §1 says what changed → §2 gives the four elements → §4 lists the unfinished item and week → §6 has that week. If four chapters disagree, the report loses PO(d) evidence.")
    c.fill = fill("FFF1D6")
    c.font = font(10, True, "8A5B00")
    c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[r].height = 40
    setup_print(ws, 7, r)


def sheet_gaps(wb: Workbook) -> None:
    ws = wb.create_sheet("Proposal Gaps")
    title_block(
        ws,
        "Proposal O1-O7  ·  gap closure",
        "Current state on 2026-11-19; use this sheet to decide what is implemented, what is a scope change, and what is honest 'not yet validated'.",
        9,
    )
    widths(ws, {"A": 8, "B": 38, "C": 28, "D": 34, "E": 40, "F": 14, "G": 30, "H": 12, "I": 13})
    header_row(ws, 4, ["Ref", "Proposal commitment", "Current state", "Gap", "Action", "Target week", "Acceptance", "Owner", "Status"])

    rows = [
        ("O1", "NILMTK pipeline over UK-DALE, REDD, PLAID, WHITED", "UK-DALE house1 + WHITED classification; custom HDF5 reader", "No REDD/PLAID; no house2; NILMTK deviation", "Add house2; choose REDD or PLAID; document NILMTK→custom reader", "Dec 8-Jan 15", "Two-dataset table + deviation note", "Jin", "In progress"),
        ("O2", "Reproduce Seq2Point baseline (5 Conv1D + dense)", "Baseline 30.7M, MAE 13.59 W avg; ONNX parity", "Inference-cost table not consolidated", "Add params/latency/size table", "Nov 22", "One cost table", "Yang", "Done"),
        ("O3", "Dilated conv + temporal attention", "Attention has 4×dilated residual + channel/temporal attention", "No dilated-only model; attribution missing", "Train dilated-only; compare baseline/dilated/attention", "Nov 22", "3-model ablation", "Yang", "In progress"),
        ("O4", "Class-balanced Huber as separate ablation axis", "Both attention and baseline use weighted Huber", "No MSE vs Huber comparison", "Train MSE baseline + weighted-Huber baseline", "Nov 22", "Loss ablation table", "Yang", "Planned"),
        ("O5", "MAE/RMSE/SAE/ACC/F1; ≥10% average MAE reduction", "MAE 13.59→11.42 (16.0% better); no RMSE; 1 seed", "RMSE missing; 3-seed/CI missing; sensitivity missing", "Add RMSE, seeds 7/17/42, bootstrap CI, window/loss sensitivity", "Nov 22", "Mean±SD + CI table", "Yang", "In progress"),
        ("O6", "ONNX + FastAPI + OpenAPI + JWT + SQLite/Postgres + Redis", "ONNX/FastAPI/OpenAPI/JWT/SQLite done; 21 checks", "No Redis/Postgres; no batch inference benchmark", "Implement Redis optional or scope down; document SQLite", "Jan 15", "Working compose + note", "Jin", "In progress"),
        ("O7", "Vue3 + Uni-app + replay + Modbus/MQTT + Docker + end-to-end", "Web/mobile/replay/dev Docker/21 checks done", "Modbus/MQTT stubs; Docker mounts ml; mobile push not verified", "Implement one Modbus or MQTT path; self-contained image", "Jan 15", "Live meter path + compose", "Jin/Yu", "Planned"),
        ("TEST", "End-to-end testing and evaluation", "21 API checks; no pytest/CI", "No automated tests/CI", "pytest + CI + frontend smoke", "Jan 15", "CI green", "Jin", "Planned"),
        ("EVID", "Every report number points to a commit", "Git repo exists; changes uncommitted", "No midterm tag", "Commit and tag midterm-2026-11-30", "Nov 28", "Tag + evidence index", "Jin", "Planned"),
    ]
    r = 5
    for idx, row_data in enumerate(rows):
        body_row(ws, r, list(row_data), height=58, banded=(idx % 2 == 1))
        r += 1

    add_status_validation(ws, "I", 5, r - 1)
    status_format(ws, "I", 5, r - 1)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:I{r - 1}"
    setup_print(ws, 9, r - 1)


def sheet_log(wb: Workbook) -> None:
    ws = wb.create_sheet("Biweekly Log")
    title_block(
        ws,
        "Biweekly log  ·  prepare before each professor meeting",
        "One row per meeting. Keep it factual: plan, done, evidence, blockers, next, decision needed.",
        6,
    )
    widths(ws, {"A": 14, "B": 38, "C": 44, "D": 30, "E": 38, "F": 30})
    header_row(ws, 4, ["Date", "Plan for last 2 weeks", "Done + evidence/commit", "Blockers", "Next 2 weeks", "Decision needed"])

    dates = [
        date(2026, 11, 25),
        date(2026, 12, 9),
        date(2026, 12, 23),
        date(2027, 1, 6),
        date(2027, 1, 20),
        date(2027, 2, 3),
        date(2027, 2, 17),
        date(2027, 3, 3),
        date(2027, 3, 17),
        date(2027, 3, 31),
        date(2027, 4, 14),
        date(2027, 4, 28),
        date(2027, 5, 12),
    ]
    r = 5
    for d in dates:
        body_row(ws, r, [d, "", "", "", "", ""], height=48)
        ws.cell(row=r, column=1).number_format = "yyyy-mm-dd"
        ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="top")
        r += 1

    ws.freeze_panes = "A5"
    setup_print(ws, 6, r - 1)


def main() -> None:
    wb = Workbook()
    sheet_readme(wb)
    sheet_gantt(wb)
    sheet_master(wb)
    sheet_calendar(wb)
    sheet_nov30(wb)
    sheet_gaps(wb)
    sheet_log(wb)

    wb.properties.title = "FYP Midterm & Biweekly Plan"
    wb.properties.creator = "NILM team"
    wb.properties.subject = "Proposal O1-O7, midterm report 11/30, oral 12/07, biweekly professor reports"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("wrote", OUT, "sheets:", wb.sheetnames)


if __name__ == "__main__":
    main()
