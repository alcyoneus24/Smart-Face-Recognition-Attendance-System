# Smart Face Recognition Attendance System

A computer-vision based attendance system that detects and recognises
enrolled students from a live webcam feed, verifies liveness to prevent
photo-based spoofing, and automatically logs attendance to a database —
with CSV/analytics reporting for staff.

Built for **CSE3010 – Computer Vision** (VITyarthi "Build Your Own Project").

## Overview

Traditional roll-call or RFID-card attendance is slow and easy to proxy.
This project automates the process using classical and learned computer
vision techniques covered across the course syllabus: image preprocessing,
face detection, feature extraction/embeddings, pattern classification, and
motion analysis (for liveness).

## Features

- **Face Detection** — Haar-cascade detector with preprocessing
  (grayscale conversion, Gaussian denoising, histogram equalisation).
- **Face Recognition** — 128-D deep embeddings (via `face_recognition`/dlib,
  with an OpenCV-only fallback encoder) matched by nearest-neighbour search.
- **Liveness / Anti-Spoofing** — Farneback optical-flow based motion analysis to help distinguish a live face from a static photo or screen.
- **Attendance Management** — SQLite-backed CRUD for students and daily
  attendance, with duplicate-mark prevention and late-arrival flagging.
- **Reporting & Analytics** — Per-day CSV export, overall summary CSV, and
  an attendance-percentage bar chart.
- **CLI Dashboard** — enroll students, run the live session, and generate
  reports, all from one command-line tool.

## Technologies / Tools Used

- Python 3
- OpenCV (`opencv-python`, `opencv-contrib-python`)
- `face_recognition` (dlib ResNet embeddings)
- SQLite3
- Matplotlib (charts)
- `unittest` (testing)

## Project Structure

```
facesys/
├── main.py                     # CLI entry point
├── config.py                   # Central configuration
├── requirements.txt
├── modules/
│   ├── face_detector.py        # Preprocessing + Haar-cascade detection
│   ├── face_encoder.py         # Feature extraction / embeddings
│   ├── recognizer.py           # Nearest-neighbour identity matching
│   ├── liveness_detector.py    # Optical-flow based anti-spoofing
│   ├── attendance_manager.py   # SQLite CRUD + business rules
│   ├── report_generator.py     # CSV + chart analytics
│   └── logger.py               # Shared logging utility
├── database/
│   └── schema.sql              # Table definitions
├── data/
│   ├── known_faces/<name>/     # Enrollment photos per student
│   └── attendance_logs/        # Generated CSV / chart output
├── tests/
│   ├── test_attendance_manager.py
│   └── test_face_detector.py
├── docs/
│   └── diagrams/                # Architecture, UML, ER diagrams
└── statement.md
```

## Installation & Setup

```bash
git clone <your-repo-url>
cd facesys
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** `face_recognition` depends on `dlib`, which needs CMake and a
> C++ compiler to build. If installation is difficult on your machine, the
> system will automatically fall back to a simpler OpenCV-only encoder
> (lower accuracy, but no extra dependencies).

## Usage

**1. Enroll a student** (provide 1–3 clear frontal photos):
```bash
python main.py enroll --name "Jane Doe" --roll CS101 --images photo1.jpg photo2.jpg
```

**2. Run the live attendance session:**
```bash
python main.py run
```
A window opens showing the webcam feed with bounding boxes, recognised
names, and a `LIVE`/`...` liveness tag. Press **q** to stop. Attendance is
marked automatically once a face is recognised **and** confirmed live.

**3. Generate reports:**
```bash
python main.py report --today      # today's attendance as CSV
python main.py report --summary    # overall summary CSV + bar chart
```

**4. List enrolled students:**
```bash
python main.py list-students
```

## Testing

```bash
python -m unittest discover -s tests -v
```

Tests cover the attendance database CRUD logic (enroll, duplicate
prevention, marking rules) and the face-detector preprocessing pipeline,
using synthetic images and a temporary throwaway database so they never
touch real data.

## Screenshots

The system was tested using a live webcam and successfully demonstrated:

- Live face detection, recognition, and liveness verification
- Automatic attendance marking and duplicate prevention
- Daily attendance CSV generation
- Attendance summary and percentage chart generation
- Automated unit testing with 9 passing tests

## Future Enhancements

- Replace Haar cascade with a DNN-based face detector (e.g. SSD/RetinaFace)
  for better accuracy under pose/occlusion variation.
- Add a proper liveness model (e.g. blink-based EAR from facial landmarks)
  instead of the coarse optical-flow heuristic.
- Web-based dashboard (Flask/Streamlit) instead of a CLI.
- Multi-camera / classroom-scale deployment with face tracking across frames.

## License

This project was created for academic purposes as part of the CSE3010
Computer Vision course.