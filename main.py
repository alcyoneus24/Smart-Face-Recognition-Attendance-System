"""
main.py
-------
Command-line entry point for the Smart Face Recognition Attendance System.

Usage:
    python main.py enroll --name "Jane Doe" --roll CS101 --images path/to/photo1.jpg [more...]
    python main.py run                     # start the live webcam attendance session
    python main.py report --today          # export today's attendance as CSV
    python main.py report --summary        # export overall summary + chart
    python main.py list-students
"""

import argparse
import os
import shutil
import sys
import time
from datetime import datetime

import cv2

import config
from modules.attendance_manager import AttendanceManager
from modules.face_detector import FaceDetector
from modules.face_encoder import FaceEncoder
from modules.liveness_detector import LivenessDetector
from modules.logger import get_logger
from modules.recognizer import Recognizer
from modules.report_generator import ReportGenerator

log = get_logger("main")


# ---------------------------------------------------------------------- #
def cmd_enroll(args):
    manager = AttendanceManager()
    person_dir = os.path.join(config.KNOWN_FACES_DIR, args.name)
    os.makedirs(person_dir, exist_ok=True)

    for i, img_path in enumerate(args.images):
        if not os.path.isfile(img_path):
            print(f"  [skip] not found: {img_path}")
            continue
        dest = os.path.join(person_dir, f"{args.name}_{i}{os.path.splitext(img_path)[1]}")
        shutil.copy(img_path, dest)

    try:
        manager.add_student(args.name, roll_number=args.roll or "", email=args.email or "")
    except ValueError as e:
        print(f"  [warn] {e}")

    print("Rebuilding face encodings, this may take a moment...")
    Recognizer().rebuild_encodings()
    print(f"Enrolled '{args.name}' with {len(args.images)} photo(s).")


def cmd_run(args):
    manager = AttendanceManager()
    recognizer = Recognizer()
    liveness = LivenessDetector()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 20)

    if not cap.isOpened():
        print("ERROR: could not access the webcam.")
        sys.exit(1)

    print("Starting live attendance session. Press 'q' to quit.")

    frame_count = 0
    last_marked_at = {}

    # Cache the latest recognition result so the label
    # remains visible between expensive recognition frames.
    cached_results = []

    while True:
        ok, frame = cap.read()

        if not ok:
            log.error("Failed to read frame from webcam.")
            break

        frame_count += 1

        # ------------------------------------------------------------ #
        # Run the expensive face recognition only every Nth frame.
        # ------------------------------------------------------------ #
        if frame_count % config.PROCESS_EVERY_N_FRAMES == 0:

            cached_results = []

            faces = recognizer.detector.detect(frame)

            for face in faces:
                x, y, w, h = face.box

                vec = recognizer.encoder.encode(face.aligned_face)

                name, distance = (
                    (None, float("inf"))
                    if vec is None
                    else recognizer.identify(vec)
                )

                gray_face = cv2.cvtColor(
                    face.aligned_face,
                    cv2.COLOR_BGR2GRAY
                )

                is_live = liveness.check(
                    gray_face,
                    face.box
                )

                label = name if name else "Unknown"

                color = (
                    (0, 200, 0)
                    if name
                    else (0, 0, 255)
                )

                cached_results.append({
                    "box": (x, y, w, h),
                    "label": label,
                    "distance": distance,
                    "is_live": is_live,
                    "color": color,
                })

                # ---------------------------------------------------- #
                # Mark attendance only when recognition + liveness
                # conditions are satisfied.
                # ---------------------------------------------------- #
                if name and is_live:
                    now = time.time()
                    cooldown = config.MIN_MINUTES_BETWEEN_MARKS * 60

                    if now - last_marked_at.get(name, 0) > cooldown:
                        message = manager.mark_attendance(
                            name,
                            confidence=1 - min(distance, 1)
                        )

                        print(message)
                        last_marked_at[name] = now

        # ------------------------------------------------------------ #
        # ALWAYS draw the latest cached recognition result.
        # This is what stops the label from blinking.
        # ------------------------------------------------------------ #
        for result in cached_results:

            x, y, w, h = result["box"]
            label = result["label"]
            distance = result["distance"]
            is_live = result["is_live"]
            color = result["color"]

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                color,
                2
            )

            if distance != float("inf"):
                tag = f"{label} ({distance:.2f})"
            else:
                tag = label

            tag += " LIVE" if is_live else " ..."

            # Keep text inside the visible image area.
            text_y = max(25, y - 10)

            cv2.putText(
                frame,
                tag,
                (x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        cv2.imshow(
            "Attendance - press q to quit",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

def cmd_report(args):
    manager = AttendanceManager()
    reporter = ReportGenerator(manager)

    if args.today:
        path = reporter.export_daily_csv()
        print(f"Today's attendance exported to: {path}")
    if args.summary:
        csv_path = reporter.export_summary_csv()
        chart_path = reporter.plot_attendance_percentage()
        print(f"Summary exported to: {csv_path}")
        if chart_path:
            print(f"Chart saved to: {chart_path}")


def cmd_list_students(args):
    manager = AttendanceManager()
    students = manager.list_students()
    if not students:
        print("No students enrolled yet.")
        return
    print(f"{'ID':<4}{'Name':<20}{'Roll No':<15}{'Enrolled On'}")
    for sid, name, roll, email, enrolled_on in students:
        print(f"{sid:<4}{name:<20}{(roll or '-'): <15}{enrolled_on}")


# ---------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smart Face Recognition Attendance System")
    sub = parser.add_subparsers(dest="command", required=True)

    p_enroll = sub.add_parser("enroll", help="Enroll a new student")
    p_enroll.add_argument("--name", required=True)
    p_enroll.add_argument("--roll", required=False)
    p_enroll.add_argument("--email", required=False)
    p_enroll.add_argument("--images", nargs="+", required=True)
    p_enroll.set_defaults(func=cmd_enroll)

    p_run = sub.add_parser("run", help="Start the live webcam attendance session")
    p_run.set_defaults(func=cmd_run)

    p_report = sub.add_parser("report", help="Generate attendance reports")
    p_report.add_argument("--today", action="store_true")
    p_report.add_argument("--summary", action="store_true")
    p_report.set_defaults(func=cmd_report)

    p_list = sub.add_parser("list-students", help="List all enrolled students")
    p_list.set_defaults(func=cmd_list_students)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
