from __future__ import annotations

from openpyxl import load_workbook

PATH = r"NILM\MIDTERM_PLAN_2026-11-19.xlsx"
wb = load_workbook(PATH)

# Master Plan: mark the first-sprint evidence tasks done.
ws = wb["Master Plan"]
for row in range(5, ws.max_row + 1):
    task = str(ws.cell(row=row, column=5).value or "")
    if "Train dilated-only" in task:
        ws.cell(row=row, column=9, value="Done")
        ws.cell(row=row, column=10, value="commit 8ae56fd; MODEL_EVIDENCE.md")
    elif "House 2" in task:
        ws.cell(row=row, column=9, value="Done")
        ws.cell(row=row, column=10, value="cross_house_house2.json; 44,141 windows")

# Proposal gaps: update the evidence-related objectives.
ws = wb["Proposal Gaps"]
for row in range(5, ws.max_row + 1):
    ref = str(ws.cell(row=row, column=1).value or "")
    if ref == "O3":
        ws.cell(row=row, column=9, value="Done")
        ws.cell(row=row, column=7, value="3-model MSE ablation: 0.797/0.789/0.786")
    elif ref == "O4":
        ws.cell(row=row, column=9, value="Done")
        ws.cell(row=row, column=7, value="2x2 loss table; MSE > weighted Huber")
    elif ref == "O5":
        ws.cell(row=row, column=9, value="In progress")
        ws.cell(row=row, column=7, value="MAE -16.1%; RMSE + 95% CI done; sensitivity pending")
    elif ref == "O1":
        ws.cell(row=row, column=9, value="In progress")
        ws.cell(row=row, column=7, value="house2 cross-house done; REDD/PLAID pending")
    elif ref == "EVID":
        ws.cell(row=row, column=9, value="Done")
        ws.cell(row=row, column=7, value="tag midterm-2026-11-30-evidence")

wb.save(PATH)
print("updated", PATH)
