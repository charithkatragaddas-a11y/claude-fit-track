import customtkinter as ctk

from db import Database
from login import LoginWindow
from tabs.log_tab import LogTab
from tabs.history_tab import HistoryTab
from tabs.report_tab import ReportTab

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FitTrackApp(ctk.CTk):

    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.title(f"FitTrack — {username}")
        self.geometry("980x680")
        self.minsize(860, 580)

        db = Database()

        self.tabview = ctk.CTkTabview(self, anchor="nw")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)

        for name in ("Log Workout", "History", "Monthly Report"):
            self.tabview.add(name)

        self.history_tab = HistoryTab(self.tabview.tab("History"), db, user_id)
        self.report_tab  = ReportTab(self.tabview.tab("Monthly Report"), db, user_id)
        self.log_tab     = LogTab(
            self.tabview.tab("Log Workout"),
            db,
            user_id,
            on_change=self._on_workout_change,
        )

        self.after(0, lambda: self.state("zoomed"))

    def _on_workout_change(self):
        self.history_tab.refresh()
        self.report_tab.refresh()


if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()

    if login.user_id is None:
        raise SystemExit

    app = FitTrackApp(login.user_id, login.username)
    app.mainloop()
