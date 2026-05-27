import customtkinter as ctk

from db import Database
from tabs.log_tab import LogTab
from tabs.history_tab import HistoryTab
from tabs.report_tab import ReportTab

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# The main application window. It inherits from ctk.CTk, which is the
# CustomTkinter version of a standard tkinter root window. Everything
# visible in the app lives inside this class.
class FitTrackApp(ctk.CTk):

    # Called automatically when FitTrackApp() is created. Sets up the
    # window size, creates the tab bar, and builds each of the three tabs.
    # History and Report are built before Log so the Log tab can reference
    # them when wiring up the on_change callback.
    def __init__(self):
        super().__init__()
        self.title("FitTrack")
        self.geometry("980x680")
        self.minsize(860, 580)

        db = Database()

        self.tabview = ctk.CTkTabview(self, anchor="nw")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)

        for name in ("Log Workout", "History", "Monthly Report"):
            self.tabview.add(name)

        self.history_tab = HistoryTab(self.tabview.tab("History"), db)
        self.report_tab  = ReportTab(self.tabview.tab("Monthly Report"), db)
        self.log_tab     = LogTab(
            self.tabview.tab("Log Workout"),
            db,
            on_change=self._on_workout_change,
        )

        # self.after(0, ...) schedules the call to happen on the first
        # event-loop tick — after all widgets are drawn — so the window
        # maximises correctly instead of fighting the geometry() call.
        self.after(0, lambda: self.state("zoomed"))

    # Called by LogTab whenever a workout is logged or deleted. Refreshes
    # the History and Monthly Report tabs so they show up-to-date data
    # without the user having to restart the app.
    def _on_workout_change(self):
        self.history_tab.refresh()
        self.report_tab.refresh()


# Standard Python entry-point guard. The code inside only runs when this
# file is executed directly (python main.py), not when it is imported.
if __name__ == "__main__":
    app = FitTrackApp()
    app.mainloop()
