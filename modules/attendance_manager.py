"""
attendance_manager.py
----------------------
Handles all database (CRUD) operations: enrolling students and recording /
retrieving attendance. This is the "Data input & processing" +
"CRUD operations" functional module required by the project brief.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from contextlib import contextmanager

import config
from modules.logger import get_logger

log = get_logger(__name__)


class AttendanceManager:
    def __init__(self, db_path: str = config.DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    # ------------------------------------------------------------------ #
    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
        with self._connect() as conn, open(schema_path, "r") as f:
            conn.executescript(f.read())
        log.info("Database initialised at %s", self.db_path)

    # ---------------------------------------------------- Student CRUD
    def add_student(self, name: str, roll_number: str = "", email: str = "") -> int:
        # Store blanks as NULL, not "" - the roll_number column is UNIQUE and
        # multiple students without a roll number must not collide.
        roll_value = roll_number or None
        email_value = email or None
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "INSERT INTO students (name, roll_number, email) VALUES (?, ?, ?)",
                    (name, roll_value, email_value),
                )
                self._audit(conn, "ENROLL", f"Enrolled student '{name}'")
                return cur.lastrowid
        except sqlite3.IntegrityError as e:
            log.error("Failed to add student %s: %s", name, e)
            raise ValueError(f"Student '{name}' already exists.") from e

    def get_student_by_name(self, name: str) -> Optional[Tuple]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT student_id, name, roll_number, email FROM students WHERE name = ?",
                (name,),
            ).fetchone()
        return row

    def list_students(self) -> List[Tuple]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT student_id, name, roll_number, email, enrolled_on FROM students ORDER BY name"
            ).fetchall()

    def delete_student(self, name: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM students WHERE name = ?", (name,))
            self._audit(conn, "DELETE_STUDENT", f"Removed student '{name}'")
            return cur.rowcount > 0

    # ------------------------------------------------------- Attendance
    def mark_attendance(self, name: str, confidence: float) -> str:
        """
        Marks attendance for `name` for *today*, applying the
        'no duplicate mark' and 'late-arrival' business rules.
        Returns a human-readable status message.
        """
        student = self.get_student_by_name(name)
        if student is None:
            return f"'{name}' is not an enrolled student."

        student_id = student[0]
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        now_time = now.strftime("%H:%M:%S")

        status = "LATE" if now_time > config.LATE_AFTER_TIME + ":00" else "PRESENT"

        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO attendance (student_id, date, time_in, status, confidence) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (student_id, today, now_time, status, confidence),
                )
                self._audit(conn, "ATTENDANCE", f"{name} marked {status} at {now_time}")
            log.info("%s marked %s at %s (confidence=%.3f)", name, status, now_time, confidence)
            return f"{name}: {status} at {now_time}"
        except sqlite3.IntegrityError:
            # UNIQUE(student_id, date) constraint -> already marked today
            return f"{name} has already been marked present today."

    def get_attendance_for_date(self, date: str) -> List[Tuple]:
        with self._connect() as conn:
            return conn.execute(
                """
                SELECT s.name, a.time_in, a.status, a.confidence
                FROM attendance a JOIN students s ON a.student_id = s.student_id
                WHERE a.date = ? ORDER BY a.time_in
                """,
                (date,),
            ).fetchall()

    def get_attendance_summary(self) -> List[Tuple]:
        """Aggregate attendance % per student across all recorded days."""
        with self._connect() as conn:
            total_days = conn.execute(
                "SELECT COUNT(DISTINCT date) FROM attendance"
            ).fetchone()[0] or 1
            return conn.execute(
                """
                SELECT s.name,
                       COUNT(a.attendance_id) AS days_present,
                       ROUND(100.0 * COUNT(a.attendance_id) / ?, 1) AS attendance_pct
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id
                GROUP BY s.student_id
                ORDER BY attendance_pct DESC
                """,
                (total_days,),
            ).fetchall()

    # ------------------------------------------------------------------ #
    def _audit(self, conn: sqlite3.Connection, event_type: str, description: str):
        conn.execute(
            "INSERT INTO audit_log (event_type, description) VALUES (?, ?)",
            (event_type, description),
        )
