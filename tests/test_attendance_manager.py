"""
test_attendance_manager.py
Unit tests for the AttendanceManager (database) module using a temporary
throw-away SQLite file, so tests never touch real attendance data.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.attendance_manager import AttendanceManager  # noqa: E402


class TestAttendanceManager(unittest.TestCase):
    def setUp(self):
        self.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_db.close()
        self.manager = AttendanceManager(db_path=self.tmp_db.name)

    def tearDown(self):
        os.unlink(self.tmp_db.name)

    def test_add_and_get_student(self):
        self.manager.add_student("Alice", roll_number="CS001")
        student = self.manager.get_student_by_name("Alice")
        self.assertIsNotNone(student)
        self.assertEqual(student[1], "Alice")

    def test_duplicate_student_raises(self):
        self.manager.add_student("Bob", roll_number="CS002")
        with self.assertRaises(ValueError):
            self.manager.add_student("Bob", roll_number="CS003")

    def test_mark_attendance_unknown_student(self):
        result = self.manager.mark_attendance("Ghost", confidence=0.9)
        self.assertIn("not an enrolled student", result)

    def test_mark_attendance_success_and_duplicate(self):
        self.manager.add_student("Carol", roll_number="CS004")
        first = self.manager.mark_attendance("Carol", confidence=0.95)
        second = self.manager.mark_attendance("Carol", confidence=0.95)
        self.assertIn("Carol", first)
        self.assertIn("already been marked", second)

    def test_list_students_sorted(self):
        self.manager.add_student("Zara")
        self.manager.add_student("Amit")
        names = [row[1] for row in self.manager.list_students()]
        self.assertEqual(names, sorted(names))

    def test_delete_student(self):
        self.manager.add_student("Dave")
        self.assertTrue(self.manager.delete_student("Dave"))
        self.assertIsNone(self.manager.get_student_by_name("Dave"))


if __name__ == "__main__":
    unittest.main()
