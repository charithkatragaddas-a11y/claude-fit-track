import calendar
from datetime import date

import customtkinter as ctk

from config import STATUS_COLORS, THRESHOLD_TOO_MUCH, THRESHOLD_NORMAL, muscle_status
from db import Database
from exercises import EXERCISES, MUSCLE_GROUPS
from ui_helpers import clear_frame


# Builds and manages the "Monthly Report" tab. For a selected month and year
# it totals the volume logged per muscle group, displays a colour-coded
# progress bar for each muscle, and shows a recommendations box at the bottom
# calling out any muscles that are overtrained, undertrained, or neglected.
class ReportTab:

    # Sets up the tab. 'parent' is the CTk frame provided by the tab view
    # and 'db' is the shared Database instance used to fetch workout records.
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self._build()

    # Creates the month/year selector dropdowns, the colour legend, and the
    # scrollable results area. Called once on startup.
    def _build(self):
        top = ctk.CTkFrame(self.parent, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(12, 0))

        ctk.CTkLabel(top, text="Month:", font=ctk.CTkFont(size=13)).pack(
            side="left", padx=(0, 10)
        )
        months = [calendar.month_name[i] for i in range(1, 13)]
        self.month_combo = ctk.CTkComboBox(
            top, values=months, width=140,
            command=lambda _: self.refresh(),
        )
        self.month_combo.set(calendar.month_name[date.today().month])
        self.month_combo.pack(side="left", padx=(0, 10))

        years = [str(y) for y in range(date.today().year - 2, date.today().year + 1)]
        self.year_combo = ctk.CTkComboBox(
            top, values=years, width=95,
            command=lambda _: self.refresh(),
        )
        self.year_combo.set(str(date.today().year))
        self.year_combo.pack(side="left")

        # Colour legend so the user knows what each bar colour means
        legend = ctk.CTkFrame(self.parent, fg_color="transparent")
        legend.pack(fill="x", padx=15, pady=(8, 4))
        for status, color in STATUS_COLORS.items():
            ctk.CTkLabel(legend, text="●", text_color=color,
                         font=ctk.CTkFont(size=15)).pack(side="left", padx=(10, 2))
            ctk.CTkLabel(legend, text=status,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 14))

        self.scroll = ctk.CTkScrollableFrame(self.parent)
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.refresh()

    # Clears the results area and recalculates volume for every muscle group
    # in the selected month. Draws a progress bar row for each muscle and
    # a recommendations box at the bottom if any muscles are out of range.
    # Called on startup, when the month/year changes, and on workout changes.
    def refresh(self):
        clear_frame(self.scroll)

        month_idx = list(calendar.month_name).index(self.month_combo.get())
        year = int(self.year_combo.get())
        _, last_day = calendar.monthrange(year, month_idx)
        start = f"{year}-{month_idx:02d}-01"
        end   = f"{year}-{month_idx:02d}-{last_day:02d}"

        rows = self.db.get_workouts_range(start, end)

        # Build a running total of volume per muscle.
        # Primary muscles receive the full volume; secondary muscles get half,
        # since they are not the main focus of the exercise.
        muscle_vol = {m: 0 for m in MUSCLE_GROUPS}
        for d, ex, num_sets, total_reps in rows:
            data = EXERCISES.get(ex, {})
            for m in data.get("primary", []):
                if m in muscle_vol:
                    muscle_vol[m] += total_reps
            for m in data.get("secondary", []):
                if m in muscle_vol:
                    muscle_vol[m] += total_reps // 2

        ctk.CTkLabel(
            self.scroll,
            text=f"{calendar.month_name[month_idx]} {year} — Muscle Volume Report",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(8, 14), anchor="w")

        if not rows:
            ctk.CTkLabel(self.scroll, text="No workouts logged this month",
                         text_color="gray60").pack(pady=30)
            return

        # The highest-volume muscle is used to scale all progress bars to
        # fill the available width proportionally.
        max_vol = max(muscle_vol.values(), default=1) or 1

        # Draw one row per muscle group
        for muscle in MUSCLE_GROUPS:
            vol = muscle_vol[muscle]
            status = muscle_status(vol)
            bar_color = STATUS_COLORS[status]

            row_frame = ctk.CTkFrame(self.scroll, fg_color=("gray88", "gray18"))
            row_frame.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row_frame, text=muscle, width=115, anchor="w",
                font=ctk.CTkFont(size=13),
            ).pack(side="left", padx=(15, 6), pady=11)

            bar_wrap = ctk.CTkFrame(row_frame, fg_color="transparent")
            bar_wrap.pack(side="left", fill="x", expand=True, padx=(0, 8))
            bar = ctk.CTkProgressBar(bar_wrap, height=16, progress_color=bar_color)
            bar.pack(fill="x", pady=12)
            bar.set(vol / max_vol)

            ctk.CTkLabel(
                row_frame, text=str(vol), width=65, anchor="e",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#5BC8F5" if vol > 0 else "gray60",
            ).pack(side="left", padx=(0, 4))

            ctk.CTkLabel(
                row_frame, text=status, width=110, anchor="w",
                text_color=bar_color, font=ctk.CTkFont(size=12),
            ).pack(side="left", padx=(6, 15))

        # Classify muscles into three groups for the recommendations box
        overtrained  = [m for m, v in muscle_vol.items() if v >= THRESHOLD_TOO_MUCH]
        undertrained = [m for m, v in muscle_vol.items() if 0 < v < THRESHOLD_NORMAL]
        neglected    = [m for m, v in muscle_vol.items() if v == 0]

        tips = []
        if overtrained:
            tips.append(("Too much volume for:", ", ".join(overtrained),
                          "Reduce frequency or sets for these muscles."))
        if undertrained:
            tips.append(("Low volume for:", ", ".join(undertrained),
                          "Add more sets or exercises targeting these muscles."))
        if neglected:
            tips.append(("Not trained this month:", ", ".join(neglected),
                          "Consider adding exercises for balanced development."))

        # Only draw the recommendations box if there is something to say
        if not tips:
            return

        box = ctk.CTkFrame(
            self.scroll, fg_color=("gray84", "gray22"),
            border_color=("gray70", "gray35"), border_width=1,
        )
        box.pack(fill="x", pady=(12, 4))
        ctk.CTkLabel(
            box, text="Recommendations", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(12, 4), padx=16, anchor="w")

        for heading, muscles_str, advice in tips:
            line_frame = ctk.CTkFrame(box, fg_color="transparent")
            line_frame.pack(fill="x", padx=16, pady=(2, 4))
            ctk.CTkLabel(line_frame, text=f"• {heading}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="gray80").pack(anchor="w")
            ctk.CTkLabel(line_frame, text=f"  {muscles_str}",
                         font=ctk.CTkFont(size=12),
                         wraplength=700, justify="left").pack(anchor="w")
            ctk.CTkLabel(line_frame, text=f"  → {advice}",
                         font=ctk.CTkFont(size=11),
                         text_color="gray60").pack(anchor="w")

        ctk.CTkFrame(box, height=10, fg_color="transparent").pack()
