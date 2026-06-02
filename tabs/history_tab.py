from datetime import date, timedelta

import customtkinter as ctk

from db import Database
from exercises import EXERCISES
from ui_helpers import make_table_header, clear_frame


# Builds and manages the "History" tab. Displays a filterable list of every
# exercise the user has logged, grouped by date. The user can switch between
# This Week, This Month, and All Time views using the radio buttons at the top.
class HistoryTab:

    # Sets up the tab. 'parent' is the CTk frame provided by the tab view
    # and 'db' is the shared Database instance used to fetch workout records.
    def __init__(self, parent, db: Database, user_id: int):
        self.parent = parent
        self.db = db
        self.user_id = user_id
        self._build()

    # Creates all the widgets for the History tab: the filter bar, the column
    # header, and the scrollable list area. Called once on startup.
    def _build(self):
        filter_bar = ctk.CTkFrame(self.parent, fg_color="transparent")
        filter_bar.pack(fill="x", padx=15, pady=(12, 6))

        ctk.CTkLabel(filter_bar, text="Show:", font=ctk.CTkFont(size=13)).pack(
            side="left", padx=(0, 12)
        )
        self.history_filter = ctk.StringVar(value="This Month")
        for opt in ("This Week", "This Month", "All Time"):
            ctk.CTkRadioButton(
                filter_bar, text=opt, variable=self.history_filter,
                value=opt, command=self.refresh,
            ).pack(side="left", padx=10)

        make_table_header(
            self.parent,
            [("Date", 110), ("Exercise", 210), ("Sets", 60),
             ("Volume", 80), ("Muscles (primary)", 230)],
        )

        self.scroll = ctk.CTkScrollableFrame(self.parent)
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.refresh()

    # Clears the list and reloads workout data from the database using
    # whichever filter is currently selected. Called on startup, when the
    # filter changes, and whenever the Log tab notifies of a workout change.
    def refresh(self):
        clear_frame(self.scroll)
        today = date.today()
        filt = self.history_filter.get()

        if filt == "This Week":
            start = today - timedelta(days=today.weekday())
            rows = self.db.get_workouts_range(start.isoformat(), today.isoformat(), self.user_id)
        elif filt == "This Month":
            rows = self.db.get_workouts_range(
                today.replace(day=1).isoformat(), today.isoformat(), self.user_id
            )
        else:
            rows = self.db.get_all_workouts(self.user_id)

        if not rows:
            ctk.CTkLabel(self.scroll, text="No workouts found",
                         text_color="gray60").pack(pady=30)
            return

        for row in rows:
            self._render_row(self.scroll, row)

    # Draws a single row in the history list. 'row' is a tuple of
    # (date, exercise, num_sets, total_reps) returned by the database.
    # 'total_reps' is the volume — the sum of reps across all sets.
    @staticmethod
    def _render_row(parent, row):
        d, ex, num_sets, total_reps = row
        muscles = ", ".join(EXERCISES.get(ex, {}).get("primary", ["?"]))
        frame = ctk.CTkFrame(parent, fg_color=("gray88", "gray18"))
        frame.pack(fill="x", pady=2)

        for text, width, color in [
            (d,              110, None),
            (ex,             210, None),
            (str(num_sets),   60, None),
            (str(total_reps), 80, "#5BC8F5"),
        ]:
            ctk.CTkLabel(frame, text=text, width=width, anchor="w",
                         text_color=color).pack(side="left", padx=(8, 0), pady=7)

        ctk.CTkLabel(frame, text=muscles, width=230, anchor="w",
                     text_color="gray60").pack(side="left", padx=(8, 8), pady=7)
