import tkinter as tk
from datetime import date

import customtkinter as ctk

from db import Database
from exercises import EXERCISES
from ui_helpers import clear_frame


# Builds and manages the "Log Workout" tab. The left panel is an exercise
# picker; the right panel is a session builder where the user adds exercises,
# enters reps for each individual set, and then logs the whole session at once.
# A "Logged Today" summary at the bottom shows what has already been saved.
class LogTab:

    # Sets up the tab. 'parent' is the CTk frame provided by the tab view,
    # 'db' is the Database instance shared across all tabs, and 'on_change'
    # is a callback function that gets called after any workout is saved or
    # deleted so the History and Report tabs can refresh themselves.
    def __init__(self, parent, db: Database, on_change):
        self.parent = parent
        self.db = db
        self.on_change = on_change
        self._exercises_sorted = sorted(EXERCISES.keys())
        # _session holds the exercises the user is currently building.
        # Keys are exercise names; values are lists of StringVars (one per set).
        self._session: dict[str, list[ctk.StringVar]] = {}
        self._build()

    # ------------------------------------------------------------------ #
    #  Layout                                                              #
    # ------------------------------------------------------------------ #

    # Creates all the widgets for the Log tab — the left exercise-picker
    # panel and the right session-builder panel. Called once on startup.
    def _build(self):
        # ── left panel: exercise picker ─────────────────────────────────
        left = ctk.CTkFrame(self.parent, width=310)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        ctk.CTkLabel(
            left, text="Log Workout", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(22, 4), padx=20)
        ctk.CTkLabel(
            left,
            text=date.today().strftime("%A, %B %d %Y"),
            text_color="#FFD700",
            font=ctk.CTkFont(size=13),
        ).pack(padx=20)

        ctk.CTkLabel(left, text="Exercise", anchor="w").pack(
            padx=20, pady=(18, 4), fill="x"
        )
        self.exercise_var = ctk.StringVar(value=self._exercises_sorted[0])
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_exercises())


        ctk.CTkEntry(
            left,
            textvariable=self.search_var,
            placeholder_text="Search exercises...",
            width=270,
        ).pack(padx=20, pady=(0, 6))
        list_outer = ctk.CTkFrame(left, fg_color=("gray75", "gray20"), corner_radius=8)
        list_outer.pack(padx=20, fill="x")

        scrollbar = tk.Scrollbar(list_outer, orient="vertical", width=12)
        self.exercise_listbox = tk.Listbox(
            list_outer,
            yscrollcommand=scrollbar.set,
            bg="#2b2b2b",
            fg="#DCE4EE",
            selectbackground="#1f6aa5",
            selectforeground="white",
            font=("Segoe UI", 12),
            relief="flat",
            bd=0,
            height=8,
            activestyle="none",
            highlightthickness=0,
            exportselection=False,
        )
        scrollbar.config(command=self.exercise_listbox.yview)
        scrollbar.pack(side="right", fill="y", pady=4, padx=(0, 4))
        self.exercise_listbox.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)

        for ex in self._exercises_sorted:
            self.exercise_listbox.insert("end", ex)
        self.exercise_listbox.selection_set(0)
        self.exercise_listbox.bind("<<ListboxSelect>>", self._on_exercise_select)

        self.muscle_preview = ctk.CTkLabel(
            left, text="", text_color="#FFD700",
            font=ctk.CTkFont(size=13), wraplength=260,
        )
        self.muscle_preview.pack(padx=20, pady=(6, 0))
        self._update_muscle_preview()

        ctk.CTkLabel(
            left,
            text="working sets only  •  exclude warm-ups",
            font=ctk.CTkFont(size=13),
            text_color="#FFD700",
        ).pack(pady=(8, 0))

        ctk.CTkButton(
            left, text="Add to Session", height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._add_exercise_to_session,
        ).pack(padx=20, pady=(14, 0), fill="x")

        self.status_label = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(8, 0))

        # ── right panel: session builder + today's log ──────────────────
        right = ctk.CTkFrame(self.parent)
        right.pack(side="left", fill="both", expand=True)

        # Header row: title on the left, Log Session button on the right
        hdr = ctk.CTkFrame(right, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(14, 6))
        ctk.CTkLabel(
            hdr, text="Session Builder", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        ctk.CTkButton(
            hdr, text="Log Session", height=36, width=130,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._log_session,
        ).pack(side="right")

        # The scrollable area where exercise cards appear as the user adds them
        self._builder_scroll = ctk.CTkScrollableFrame(right)
        self._builder_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 4))

        # Visual divider between the session builder and the today summary
        ctk.CTkFrame(right, height=1, fg_color=("gray70", "gray30")).pack(
            fill="x", padx=15, pady=(6, 4)
        )

        # Fixed-height panel at the bottom showing what is already in the DB for today
        ctk.CTkLabel(
            right, text="Logged Today", font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(0, 4))

        self.today_scroll = ctk.CTkScrollableFrame(right, height=160)
        self.today_scroll.pack(fill="x", padx=15, pady=(0, 12))

        self._render_session_builder()
        self._refresh_today_summary()

    # ------------------------------------------------------------------ #
    #  Exercise picker                                                     #
    # ------------------------------------------------------------------ #

    # Fired when the user clicks an item in the exercise listbox. Updates
    # exercise_var with the selected name and refreshes the muscle preview.
    def _on_exercise_select(self, event=None):
        sel = self.exercise_listbox.curselection()
        if sel:
            self.exercise_var.set(self.exercise_listbox.get(sel[0]))
            self._update_muscle_preview()

    # Filters the exercise listbox based on what the user has typed.
    # Shows only exercises whose names start with the search text.
    # Clears and repopulates the listbox on every keystroke.
    def _filter_exercises(self):
        search = self.search_var.get().lower()
        self.exercise_listbox.delete(0, "end")
        for ex in self._exercises_sorted:
            if ex.lower().startswith(search):
                self.exercise_listbox.insert("end", ex)
        if self.exercise_listbox.size() > 0:
            self.exercise_listbox.selection_set(0)
            self._on_exercise_select()

    # Reads the currently selected exercise from exercise_var, looks up its
    # primary and secondary muscles in the EXERCISES dict, and updates the
    # muscle_preview label so the user can see which muscles they are targeting.
    def _update_muscle_preview(self):
        ex = self.exercise_var.get()
        data = EXERCISES.get(ex, {})
        primary = ", ".join(data.get("primary", []))
        secondary = data.get("secondary", [])
        text = f"Primary: {primary}"
        if secondary:
            text += f"  |  Secondary: {', '.join(secondary)}"
        self.muscle_preview.configure(text=text)

    # ------------------------------------------------------------------ #
    #  Session builder actions                                             #
    # ------------------------------------------------------------------ #

    # Adds the currently selected exercise to self._session with one blank
    # set. Shows an error if the exercise is already in the session. Then
    # redraws the session builder to show the new card.
    def _add_exercise_to_session(self):
        ex = self.exercise_var.get()
        if ex not in EXERCISES:
            self._flash_status("Pick an exercise from the list", "#F44336")
            return
        if ex in self._session:
            self._flash_status(f"{ex} is already in your session", "#FF9800")
            return
        self._session[ex] = [ctk.StringVar(value="")]
        self._render_session_builder()

    # Appends a new blank set (a new StringVar) to the given exercise's list,
    # then redraws the session builder so a new reps input row appears.
    def _add_set(self, exercise: str):
        self._session[exercise].append(ctk.StringVar(value=""))
        self._render_session_builder()

    # Removes a single set by its index from the given exercise. If removing
    # it would leave zero sets, the whole exercise is removed too. Then redraws.
    def _remove_set(self, exercise: str, idx: int):
        self._session[exercise].pop(idx)
        if not self._session[exercise]:
            del self._session[exercise]
        self._render_session_builder()

    # Removes an entire exercise (and all its sets) from self._session,
    # then redraws the session builder.
    def _remove_exercise(self, exercise: str):
        del self._session[exercise]
        self._render_session_builder()

    # ------------------------------------------------------------------ #
    #  Rendering                                                           #
    # ------------------------------------------------------------------ #

    # Clears the builder scroll area and redraws every exercise card from
    # scratch using the current state of self._session. Called after any
    # change to the session (add exercise, add set, remove set, etc.).
    def _render_session_builder(self):
        clear_frame(self._builder_scroll)
        if not self._session:
            ctk.CTkLabel(
                self._builder_scroll,
                text="Select an exercise and click 'Add to Session'",
                text_color="gray60",
            ).pack(pady=30)
            return
        for exercise in self._session:
            self._render_exercise_card(self._builder_scroll, exercise)

    # Draws a single exercise card inside 'parent'. The card contains the
    # exercise name, a Remove button, one reps-entry row per set, and an
    # "+ Add Set" button. The reps entries are bound to the StringVars stored
    # in self._session so their values survive a full redraw.
    def _render_exercise_card(self, parent, exercise: str):
        card = ctk.CTkFrame(parent, fg_color=("gray83", "gray22"), corner_radius=8)
        card.pack(fill="x", pady=5, padx=2)

        # Card header: exercise name + Remove button
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        ctk.CTkLabel(
            hdr, text=exercise, font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")
        ctk.CTkButton(
            hdr, text="Remove", width=72, height=26,
            fg_color="transparent",
            border_color="#F44336", border_width=1,
            text_color="#F44336",
            hover_color=("#FFE0E0", "#3D1010"),
            font=ctk.CTkFont(size=11),
            command=lambda ex=exercise: self._remove_exercise(ex),
        ).pack(side="right")

        # One row per set: "Set N" label + reps entry + optional remove button
        reps_vars = self._session[exercise]
        for i, var in enumerate(reps_vars):
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)

            ctk.CTkLabel(
                row, text=f"Set {i + 1}", width=46,
                font=ctk.CTkFont(size=12), text_color="gray70",
            ).pack(side="left")
            ctk.CTkEntry(
                row, textvariable=var, width=72, justify="center",
                font=ctk.CTkFont(size=16),
            ).pack(side="left", padx=(6, 4))
            ctk.CTkLabel(
                row, text="reps", text_color="gray60", font=ctk.CTkFont(size=12),
            ).pack(side="left")

            # Only show the ✕ remove button when there is more than one set
            if len(reps_vars) > 1:
                ctk.CTkButton(
                    row, text="✕", width=28, height=28,
                    fg_color="transparent",
                    hover_color=("gray75", "gray30"),
                    font=ctk.CTkFont(size=12),
                    command=lambda ex=exercise, idx=i: self._remove_set(ex, idx),
                ).pack(side="right")

        # Button at the bottom of the card to add another set row
        ctk.CTkButton(
            card, text="+ Add Set", height=28, anchor="w",
            fg_color="transparent",
            border_color=("gray60", "gray45"), border_width=1,
            hover_color=("gray80", "gray28"),
            font=ctk.CTkFont(size=12),
            command=lambda ex=exercise: self._add_set(ex),
        ).pack(padx=12, pady=(4, 10), anchor="w")

    # ------------------------------------------------------------------ #
    #  Logging                                                             #
    # ------------------------------------------------------------------ #

    # Validates every reps field in the session, saves the data to the
    # database, clears the session builder, and triggers a refresh of the
    # History and Monthly Report tabs via the on_change callback.
    def _log_session(self):
        if not self._session:
            self._flash_status("Add at least one exercise first", "#F44336")
            return

        exercises_data = []
        for exercise, vars_list in self._session.items():
            reps_list = []
            for i, var in enumerate(vars_list):
                try:
                    r = int(var.get())
                    if r <= 0:
                        raise ValueError
                    reps_list.append(r)
                except ValueError:
                    self._flash_status(
                        f"Set {i + 1} for {exercise}: enter a whole number > 0",
                        "#F44336",
                    )
                    return
            exercises_data.append({"exercise": exercise, "sets": reps_list})

        self.db.log_session(date.today().isoformat(), exercises_data)
        count = len(exercises_data)
        self._flash_status(
            f"Logged {count} exercise{'s' if count != 1 else ''}!", "#4CAF50"
        )
        self._session.clear()
        self._render_session_builder()
        self._refresh_today_summary()
        self.on_change()

    # Shows a temporary status message in the left panel. The message
    # disappears automatically after 3.5 seconds using self.after().
    def _flash_status(self, msg: str, color: str):
        self.status_label.configure(text=msg, text_color=color)
        self.status_label.after(3500, lambda: self.status_label.configure(text=""))

    # ------------------------------------------------------------------ #
    #  Today's summary (bottom panel)                                     #
    # ------------------------------------------------------------------ #

    # Public method called by main.py after a workout change. Delegates to
    # _refresh_today_summary so the "Logged Today" panel stays current.
    def refresh(self):
        self._refresh_today_summary()

    # Queries the database for everything logged today and redraws the
    # "Logged Today" panel at the bottom of the right side. Called after
    # logging a session or deleting an exercise.
    def _refresh_today_summary(self):
        clear_frame(self.today_scroll)
        rows = self.db.get_today_summary(date.today().isoformat())
        if not rows:
            ctk.CTkLabel(
                self.today_scroll, text="Nothing logged today yet",
                text_color="gray60",
            ).pack(pady=16)
            return
        for exercise, num_sets, total_reps in rows:
            self._render_today_row(exercise, num_sets, total_reps)

    # Draws a single read-only row in the "Logged Today" panel showing the
    # exercise name, number of sets, total volume, and a Delete button.
    def _render_today_row(self, exercise: str, num_sets: int, total_reps: int):
        frame = ctk.CTkFrame(self.today_scroll, fg_color=("gray88", "gray18"))
        frame.pack(fill="x", pady=2)

        ctk.CTkLabel(frame, text=exercise, width=200, anchor="w").pack(
            side="left", padx=(10, 0), pady=7
        )
        ctk.CTkLabel(
            frame, text=f"{num_sets} sets", width=70, anchor="w",
            text_color="gray60",
        ).pack(side="left")
        ctk.CTkLabel(
            frame, text=f"vol {total_reps}", width=80, anchor="w",
            text_color="#5BC8F5", font=ctk.CTkFont(weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            frame, text="Delete", width=64, height=26,
            fg_color="transparent",
            border_color="#F44336", border_width=1,
            text_color="#F44336",
            hover_color=("#FFE0E0", "#3D1010"),
            font=ctk.CTkFont(size=11),
            command=lambda ex=exercise: self._delete_today_exercise(ex),
        ).pack(side="right", padx=8)

    # Deletes all sets for the given exercise from today's database records,
    # redraws the "Logged Today" panel, and notifies the other tabs to refresh.
    def _delete_today_exercise(self, exercise: str):
        self.db.delete_exercise_sets(date.today().isoformat(), exercise)
        self._refresh_today_summary()
        self.on_change()
