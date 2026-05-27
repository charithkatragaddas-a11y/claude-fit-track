# Monthly volume thresholds — derived from target training profile:
#   2 working sets per muscle per session, 2 sessions/week (PPL / upper-lower), 4 weeks/month
#   Rep lower limit = 4  →  2 × 4 × 2 × 4 = 64   (floor for "normal")
#   Rep upper limit = 10 →  2 × 10 × 2 × 4 = 160  (ceiling before "too much")
THRESHOLD_TOO_MUCH = 160
THRESHOLD_NORMAL   = 64

# Maps each training status to a hex colour code used for progress bars
# and status labels in the Monthly Report tab.
STATUS_COLORS = {
    "Too much":     "#F44336",  # red
    "Normal":       "#4CAF50",  # green
    "Undertrained": "#FF9800",  # orange
    "Neglected":    "#555555",  # dark grey
}


# Takes a muscle's total monthly volume (sum of all reps for that muscle)
# and returns a string describing the training status. Used by the Monthly
# Report tab to label and colour each muscle group row.
def muscle_status(vol: int) -> str:
    if vol == 0:
        return "Neglected"
    if vol >= THRESHOLD_TOO_MUCH:
        return "Too much"
    if vol >= THRESHOLD_NORMAL:
        return "Normal"
    return "Undertrained"
