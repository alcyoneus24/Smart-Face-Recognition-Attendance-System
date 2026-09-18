"""
report_generator.py
--------------------
Analytics / reporting functional module: turns raw attendance rows into
CSV exports and summary charts for staff review.
"""

import csv
import os
from datetime import datetime
from typing import List

import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt

import config
from modules.attendance_manager import AttendanceManager
from modules.logger import get_logger

log = get_logger(__name__)


class ReportGenerator:
    def __init__(self, manager: AttendanceManager):
        self.manager = manager
        os.makedirs(config.ATTENDANCE_LOG_DIR, exist_ok=True)

    def export_daily_csv(self, date: str = None) -> str:
        date = date or datetime.now().strftime("%Y-%m-%d")
        rows = self.manager.get_attendance_for_date(date)

        out_path = os.path.join(config.ATTENDANCE_LOG_DIR, f"attendance_{date}.csv")
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Time In", "Status", "Confidence"])
            writer.writerows(rows)

        log.info("Exported daily attendance CSV -> %s (%d rows)", out_path, len(rows))
        return out_path

    def export_summary_csv(self) -> str:
        summary = self.manager.get_attendance_summary()
        out_path = os.path.join(config.ATTENDANCE_LOG_DIR, "attendance_summary.csv")
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Days Present", "Attendance %"])
            writer.writerows(summary)
        log.info("Exported attendance summary CSV -> %s", out_path)
        return out_path

    def plot_attendance_percentage(self) -> str:
        """Bar chart of attendance % per student - visual analytics."""
        summary = self.manager.get_attendance_summary()
        if not summary:
            log.warning("No attendance data available to plot.")
            return ""

        names = [row[0] for row in summary]
        pct = [row[2] for row in summary]

        plt.figure(figsize=(8, 4.5))
        bars = plt.bar(names, pct, color="#4C72B0")
        plt.ylabel("Attendance %")
        plt.title("Attendance Percentage by Student")
        plt.xticks(rotation=30, ha="right")
        plt.ylim(0, 100)
        for bar, value in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, value + 1, f"{value}%",
                      ha="center", fontsize=8)
        plt.tight_layout()

        out_path = os.path.join(config.ATTENDANCE_LOG_DIR, "attendance_chart.png")
        plt.savefig(out_path, dpi=150)
        plt.close()
        log.info("Saved attendance chart -> %s", out_path)
        return out_path
