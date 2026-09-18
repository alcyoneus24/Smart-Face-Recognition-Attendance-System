# Smart Face Recognition Attendance System

A computer-vision based attendance system that detects and recognises enrolled students from a live webcam feed, verifies liveness using optical-flow based motion analysis, and automatically logs attendance to a database with CSV and analytics reporting.

Built for **CSE3010 – Computer Vision** (VITyarthi "Build Your Own Project").

## Overview

Traditional roll-call or RFID-card attendance is slow and can allow proxy attendance.

This project automates the process using classical and learned computer vision techniques covered across the course syllabus: image preprocessing, face detection, feature extraction/embeddings, pattern classification, and motion analysis for liveness.

The system is designed for a **single-camera, controlled-lighting classroom scenario**.

## Features

- **Face Detection** — Haar-cascade detector with preprocessing using grayscale conversion, Gaussian denoising, and histogram equalisation.
- **Face Recognition** — 128-D deep embeddings using `face_recognition`/dlib, with an OpenCV-only fallback encoder, matched using nearest-neighbour search.
- **Liveness / Anti-Spoofing** — Farneback optical-flow based motion analysis to help distinguish a live face from a static photo or screen.
- **Attendance Management** — SQLite-backed student and attendance management with duplicate-mark prevention and late-arrival handling.
- **Reporting & Analytics** — Per-day CSV export, overall attendance summary CSV, and attendance-percentage bar chart.
- **CLI Dashboard** — Enroll students, run live attendance sessions, list students, and generate reports using one command-line interface.
- **Automated Testing** — Unit tests using Python `unittest` for attendance/database logic and the face-detection pipeline.

## Technologies / Tools Used

- Python 3
- OpenCV (`opencv-python`, `opencv-contrib-python`)
- `face_recognition` / dlib
- SQLite3
- Matplotlib
- `unittest`

## Project Structure

```text
facesys/
│
├── main.py                         # CLI entry point
├── config.py                       # Central configuration
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── statement.md                    # Project statement
├── .gitignore                      # Ignored runtime/personal files
│
├── modules/
│   ├── __init__.py
│   ├── face_detector.py            # Preprocessing + Haar-cascade detection
│   ├── face_encoder.py             # Feature extraction / face embeddings
│   ├── recognizer.py               # Nearest-neighbour identity matching
│   ├── liveness_detector.py        # Optical-flow based liveness
│   ├── attendance_manager.py       # SQLite CRUD + attendance rules
│   ├── report_generator.py         # CSV + chart analytics
│   └── logger.py                   # Shared logging utility
│
├── database/
│   └── schema.sql                  # Database table definitions
│
├── data/                           # Created/used locally at runtime
│   ├── enrollment/                 # Input enrollment photos
│   ├── known_faces/                # Stored enrollment images
│   ├── encodings_cache.pkl         # Generated face encodings
│   └── attendance_logs/            # Generated CSV and chart output
│
├── tests/
│   ├── test_attendance_manager.py
│   └── test_face_detector.py
│
└── docs/
    └── diagrams/
        ├── architecture.png
        ├── class_diagram.png
        ├── er_diagram.png
        ├── sequence.png
        ├── usecase.png
        └── workflow.png
```

> **Note:** Personal enrollment photographs, generated face encodings, the local SQLite database, attendance reports, and runtime logs are intentionally excluded from the GitHub repository through `.gitignore`.

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/alcyoneus24/Smart-Face-Recognition-Attendance-System.git
cd Smart-Face-Recognition-Attendance-System
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `face_recognition` depends on dlib. On some systems, installing dlib may require CMake and a C++ compiler. If the dlib-based encoder cannot be used, the project can fall back to an OpenCV-based encoder with lower recognition accuracy.

### 4. Verify the installation

Run:

```bash
python main.py list-students
```

On a fresh installation, the application automatically creates the required SQLite database.

Expected output:

```text
No students enrolled yet.
```

## How to Use

The normal workflow is:

```text
Install
   ↓
Enroll Student
   ↓
Generate Face Encodings
   ↓
Start Webcam
   ↓
Detect Face
   ↓
Recognise Face
   ↓
Check Liveness
   ↓
Mark Attendance
   ↓
Generate Reports
```

## 1. Enroll a Student

Before starting live attendance, enroll at least one student.

Prepare **1–3 clear frontal photographs** of the student.

Example:

```bash
python main.py enroll --name "Jane Doe" --roll CS101 --images photo1.jpg photo2.jpg photo3.jpg
```

For example:

```bash
python main.py enroll --name "Aditya Taiwade" --roll 24BAI10147 --images aditya1.jpg aditya2.jpg aditya3.jpg
```

During enrollment, the system:

1. Copies the enrollment photographs into the local known-face directory.
2. Adds the student to the SQLite database.
3. Detects faces from the enrollment photographs.
4. Generates face embeddings.
5. Stores the generated encoding cache.

A successful enrollment displays a message similar to:

```text
Rebuilding face encodings, this may take a moment...
Enrolled 'Jane Doe' with 3 photo(s).
```

### Recommended Enrollment Conditions

For better recognition:

- Use clear frontal face photographs.
- Ensure the face is clearly visible.
- Avoid very dark or heavily blurred images.
- Use 2–3 photographs when possible.
- Keep reasonable and consistent lighting.

## 2. List Enrolled Students

To check which students are enrolled:

```bash
python main.py list-students
```

Example:

```text
ID  Name                Roll No        Enrolled On
1   Jane Doe            CS101          2026-09-18
```

## 3. Run the Live Attendance Session

Make sure:

- A webcam is connected.
- At least one student has been enrolled.
- The virtual environment is activated.

Run:

```bash
python main.py run
```

A webcam window will open showing:

- Face bounding boxes
- Recognised student names
- Face distance
- Liveness status

Example:

```text
Jane Doe (0.22) LIVE
```

The numerical value displayed is the **face distance** used for recognition matching.

Attendance is marked automatically when the face is successfully recognised and the liveness check passes.

### Stop the live session

Press:

```text
q
```

## 4. Generate Today's Attendance Report

After running the attendance session, generate today's attendance CSV:

```bash
python main.py report --today
```

The generated file is saved in:

```text
data/attendance_logs/
```

Example:

```text
attendance_2026-09-18.csv
```

## 5. Generate Attendance Summary and Chart

To generate the overall attendance summary:

```bash
python main.py report --summary
```

This generates:

```text
data/attendance_logs/attendance_summary.csv
data/attendance_logs/attendance_chart.png
```

The summary contains information such as:

- Student name
- Number of days present
- Attendance percentage

## 6. Run Automated Tests

The project includes automated unit tests.

Run:

```bash
python -m unittest discover -s tests -v
```

The tests cover:

- Student enrollment
- Student listing
- Duplicate student validation
- Student deletion
- Successful attendance marking
- Duplicate attendance prevention
- Unknown student handling
- Face detection
- Image preprocessing

A successful test run should display:

```text
Ran 9 tests

OK
```

The tests use temporary/synthetic data where appropriate and do not depend on the real attendance database.

## Complete Usage Example

For a completely fresh installation, follow these commands in order:

### Step 1 — Clone

```bash
git clone https://github.com/alcyoneus24/Smart-Face-Recognition-Attendance-System.git
cd Smart-Face-Recognition-Attendance-System
```

### Step 2 — Create and activate the virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Enroll a student

Place 1–3 enrollment photographs in an accessible location and run:

```bash
python main.py enroll --name "Test Student" --roll TEST001 --images photo1.jpg photo2.jpg photo3.jpg
```

### Step 5 — Check enrollment

```bash
python main.py list-students
```

### Step 6 — Start live attendance

```bash
python main.py run
```

Press `q` to stop.

### Step 7 — Generate today's report

```bash
python main.py report --today
```

### Step 8 — Generate summary and chart

```bash
python main.py report --summary
```

### Step 9 — Run automated tests

```bash
python -m unittest discover -s tests -v
```

## Attendance Rules

Attendance is marked only when:

1. A face is detected.
2. The face matches an enrolled student.
3. The liveness check passes.

The system also prevents duplicate attendance marking according to the configured attendance rules.

## Troubleshooting

### Webcam cannot be accessed

Make sure:

- The webcam is connected.
- No other application is currently using the webcam.
- Windows has granted camera access to Python.

The application displays:

```text
ERROR: could not access the webcam.
```

if the webcam cannot be opened.

### No face is recognised

Try:

- Improving the lighting.
- Using clearer enrollment photographs.
- Keeping the face more frontal.
- Re-enrolling the student with 2–3 clear photographs.

### Student is already marked present

This is expected behaviour. The system prevents duplicate attendance marking according to its attendance rules.

### Dependency installation problems

If `face_recognition` or dlib installation fails, ensure that the required build tools and CMake are installed.

The project also provides an OpenCV-based fallback encoder.

## Design Documentation

The `docs/diagrams/` directory contains:

- System Architecture Diagram
- Use Case Diagram
- Workflow Diagram
- Sequence Diagram
- Class Diagram
- ER Diagram

The project statement is available in:

```text
statement.md
```

## Screenshots / Results

The system was tested using a live webcam and demonstrated:

- Live face detection
- Face recognition
- Liveness verification
- Automatic attendance marking
- Duplicate attendance prevention
- Daily attendance CSV generation
- Attendance summary generation
- Attendance percentage chart generation
- Automated unit testing with 9 passing tests

## Privacy and Data Handling

The GitHub repository does not contain personal enrollment photographs or generated attendance records.

The following data is stored locally when the system is used:

- Enrollment photographs
- Known-face images
- Face encoding cache
- SQLite attendance database
- Generated attendance CSV files
- Attendance chart
- Runtime logs

Users should only enroll photographs for which they have appropriate permission to use.

## Future Enhancements

- Replace the Haar cascade with a DNN-based face detector such as SSD or RetinaFace for improved performance under pose and occlusion variations.
- Add a dedicated liveness model such as blink-based EAR using facial landmarks instead of the current optical-flow based heuristic.
- Develop a web-based dashboard using Flask or Streamlit instead of the CLI.
- Add multi-camera and classroom-scale deployment with face tracking across frames.
- Improve recognition performance under difficult lighting conditions.
- Add role-based authentication for administrators.

## Academic Project

This project was developed for **CSE3010 – Computer Vision** at **VIT Bhopal** as part of the VITyarthi **Build Your Own Project**.