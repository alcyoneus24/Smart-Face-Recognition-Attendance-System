-- schema.sql
-- Relational schema for the Smart Face Recognition Attendance System.

CREATE TABLE IF NOT EXISTS students (
    student_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL UNIQUE,
    roll_number  TEXT UNIQUE,
    email        TEXT,
    enrolled_on  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL,
    date          TEXT NOT NULL,
    time_in       TEXT NOT NULL,
    status        TEXT NOT NULL CHECK(status IN ('PRESENT', 'LATE')),
    confidence    REAL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE(student_id, date)
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,
    description TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
