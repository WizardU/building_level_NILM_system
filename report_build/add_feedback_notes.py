from pptx import Presentation

PATH = r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计\NILM_Review_Response_11.25.pptx"
prs = Presentation(PATH)
notes = [
    "This deck only answers the review: what changed, what is still partial, and what is next. It does not repeat the system overview.",
    "Eight review comments: four closed, four partial. The table points to the slide or file with the evidence.",
    "Training: full 8-epoch train/validation curves. Validation loss stops improving on several appliances, but automatic early stopping is not implemented, so this is partial.",
    "Sample counts: the five UK-DALE appliances and the 40 WHITED classes. Microwave is 0.39% ON; 22 WHITED classes have only one device and are train-only.",
    "Microwave: threshold tuning cannot fix recall. A 25x positive-weighted MSE lifts Event F1 from 0.407 to 0.494 and recall to 0.68, but it is an offline experiment, not deployed.",
    "Architecture: input 1x599, Conv1D kernel 5, dilation 1/2/4/8, channel and temporal attention, FC output. The WHITED baseline is a 19-feature RF pipeline.",
    "F1: three models, Event and State. Attention wins Event/MAE, baseline wins State; no Seq2Seq yet, so this is partial.",
    "Red circles: truth vs prediction. Dishwasher is truly about 1.1 kW but the model gives about 0.2 kW; residual is small, so this is a recall failure.",
    "Why the numbers: UK-DALE trade-off and cross-house ranking flip; WHITED 44.1% is a strict 18/40-class, 20-device test with a long tail.",
    "Demo: four scenes and one API. Runbook is prepared; a live run-through is still required before 12/07.",
    "Next six days: freeze evidence, write the eight-chapter report, submit on 11/30, then rehearse the oral and demo.",
    "After the midterm: close proposal gaps in order: evidence, system, thesis, delivery. Do not add features before the evidence.",
    "Three decisions today: report structure, scope (REDD/PLAID vs WHITED CNN; Redis/Modbus), and live vs recorded demo.",
]
for slide, note in zip(prs.slides, notes):
    slide.notes_slide.notes_text_frame.text = note
prs.save(PATH)
print("notes added", len(notes))
