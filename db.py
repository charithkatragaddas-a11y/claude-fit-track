import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "fittrack.db"


# Handles all reading and writing to the SQLite database file (fittrack.db).
# Every method on this class is either a "write" (inserting or deleting rows)
# or a "read" (fetching rows back out). No UI code lives here — it is purely
# data access.
class Database:

    # Opens (or creates) the database file and makes sure the required
    # tables exist before any other method is called.
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self._create_tables()

    # Creates the database tables if they do not already exist.
    # The legacy 'workouts' table is kept so older database files still
    # open without errors, but the app only writes to 'workout_sets'.
    # 'workout_sets' stores one row for every individual set the user logs.
    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                date     TEXT    NOT NULL,
                exercise TEXT    NOT NULL,
                sets     INTEGER NOT NULL,
                reps     INTEGER NOT NULL,
                volume   INTEGER NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS workout_sets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                date       TEXT    NOT NULL,
                exercise   TEXT    NOT NULL,
                set_number INTEGER NOT NULL,
                reps       INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Writes                                                              #
    # ------------------------------------------------------------------ #

    # Saves a full workout session to the database. 'exercises' is a list
    # of dictionaries, each with an 'exercise' name and a 'sets' list of
    # rep counts — e.g. [{'exercise': 'Bench Press', 'sets': [6, 8, 7]}].
    # Each rep count becomes its own row in workout_sets.
    def log_session(self, date: str, exercises: list) -> None:
        for ex_data in exercises:
            for set_num, reps in enumerate(ex_data["sets"], start=1):
                self.conn.execute(
                    "INSERT INTO workout_sets (date, exercise, set_number, reps) "
                    "VALUES (?, ?, ?, ?)",
                    (date, ex_data["exercise"], set_num, reps),
                )
        self.conn.commit()

    # Deletes every set logged for a specific exercise on a specific date.
    # Used when the user clicks the Delete button in the "Logged Today" panel.
    def delete_exercise_sets(self, date: str, exercise: str) -> None:
        self.conn.execute(
            "DELETE FROM workout_sets WHERE date = ? AND exercise = ?",
            (date, exercise),
        )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Reads                                                               #
    # ------------------------------------------------------------------ #

    # Returns a summary of every exercise logged on a given date.
    # Each item in the result is (exercise, num_sets, total_reps).
    # 'total_reps' is the volume — the sum of all individual set rep counts.
    def get_today_summary(self, date: str):
        return self.conn.execute("""
            SELECT exercise, COUNT(*) AS num_sets, SUM(reps) AS total_reps
            FROM workout_sets
            WHERE date = ?
            GROUP BY exercise
            ORDER BY exercise
        """, (date,)).fetchall()

    # Returns all exercises logged between two dates (inclusive).
    # Each item is (date, exercise, num_sets, total_reps), grouped so that
    # multiple sets of the same exercise on the same day appear as one row.
    # Used by the History and Monthly Report tabs.
    def get_workouts_range(self, start: str, end: str):
        return self.conn.execute("""
            SELECT date, exercise, COUNT(*) AS num_sets, SUM(reps) AS total_reps
            FROM workout_sets
            WHERE date >= ? AND date <= ?
            GROUP BY date, exercise
            ORDER BY date DESC, exercise
        """, (start, end)).fetchall()

    # Same format as get_workouts_range but returns every row ever logged,
    # with no date filter. Used by the History tab's "All Time" view.
    def get_all_workouts(self):
        return self.conn.execute("""
            SELECT date, exercise, COUNT(*) AS num_sets, SUM(reps) AS total_reps
            FROM workout_sets
            GROUP BY date, exercise
            ORDER BY date DESC, exercise
        """).fetchall()
