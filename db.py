import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "fittrack.db"


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self._create_tables()
        self._migrate()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL UNIQUE
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS workout_sets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL DEFAULT 1,
                date       TEXT    NOT NULL,
                exercise   TEXT    NOT NULL,
                set_number INTEGER NOT NULL,
                reps       INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def _migrate(self):
        # For existing databases that pre-date the multi-user feature:
        # add the user_id column and assign all legacy rows to a 'default' user.
        cols = [row[1] for row in self.conn.execute("PRAGMA table_info(workout_sets)").fetchall()]
        if "user_id" not in cols:
            self.conn.execute("INSERT OR IGNORE INTO users (id, username) VALUES (1, 'default')")
            self.conn.execute("ALTER TABLE workout_sets ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
            self.conn.commit()

    # ------------------------------------------------------------------ #
    #  User management                                                     #
    # ------------------------------------------------------------------ #

    def get_user(self, username: str):
        return self.conn.execute(
            "SELECT id, username FROM users WHERE username = ?", (username,)
        ).fetchone()

    def create_user(self, username: str) -> int:
        cursor = self.conn.execute(
            "INSERT INTO users (username) VALUES (?)", (username,)
        )
        self.conn.commit()
        return cursor.lastrowid

    # ------------------------------------------------------------------ #
    #  Writes                                                              #
    # ------------------------------------------------------------------ #

    def log_session(self, date: str, exercises: list, user_id: int) -> None:
        for ex_data in exercises:
            for set_num, reps in enumerate(ex_data["sets"], start=1):
                self.conn.execute(
                    "INSERT INTO workout_sets (user_id, date, exercise, set_number, reps) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (user_id, date, ex_data["exercise"], set_num, reps),
                )
        self.conn.commit()

    def delete_exercise_sets(self, date: str, exercise: str, user_id: int) -> None:
        self.conn.execute(
            "DELETE FROM workout_sets WHERE user_id = ? AND date = ? AND exercise = ?",
            (user_id, date, exercise),
        )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Reads                                                               #
    # ------------------------------------------------------------------ #

    def get_today_summary(self, date: str, user_id: int):
        return self.conn.execute("""
            SELECT exercise, COUNT(*) AS num_sets, SUM(reps) AS total_reps
            FROM workout_sets
            WHERE user_id = ? AND date = ?
            GROUP BY exercise
            ORDER BY exercise
        """, (user_id, date)).fetchall()

    def get_workouts_range(self, start: str, end: str, user_id: int):
        return self.conn.execute("""
            SELECT date, exercise, COUNT(*) AS num_sets, SUM(reps) AS total_reps
            FROM workout_sets
            WHERE user_id = ? AND date >= ? AND date <= ?
            GROUP BY date, exercise
            ORDER BY date DESC, exercise
        """, (user_id, start, end)).fetchall()

    def get_all_workouts(self, user_id: int):
        return self.conn.execute("""
            SELECT date, exercise, COUNT(*) AS num_sets, SUM(reps) AS total_reps
            FROM workout_sets
            WHERE user_id = ?
            GROUP BY date, exercise
            ORDER BY date DESC, exercise
        """, (user_id,)).fetchall()
