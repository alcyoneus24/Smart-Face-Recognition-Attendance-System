# Smart Face Recognition Attendance System

This project is all about hassle-free attendance. Instead of roll call or RFID cards, we use a webcam and computer vision to spot and recognize students in real time—directly from the live feed. The system makes sure the person in front of the camera is real by checking for motion, then records attendance automatically in a database. You get CSV reports and handy analytics, too.

We built this for the **CSE3010 – Computer Vision** course as part of VITyarthi’s “Build Your Own Project” series.

## Why Even Bother?

Let’s be honest: traditional attendance is a slog. Roll calls and card swipes are slow, and anyone can pull off a proxy if they want to. This project fixes all of that—no more wasting class time or playing games with attendance.

We pulled together everything we learned in class:

- Image preprocessing
- Face detection
- Feature extraction (face embeddings)
- Pattern classification
- Motion (liveness) analysis

It’s built for a regular classroom—just one camera and decent lighting.

## What’s Inside?

- **Face Detection:** Uses Haar-cascade detection plus some image cleanup (grayscale conversion, Gaussian blur, histogram equalization).
- **Face Recognition:** Makes 128-dimension face embeddings with `face_recognition`/dlib (or pure OpenCV, if needed, though it’s less accurate). Matches use nearest-neighbor search.
- **Liveness / Anti-Spoofing:** No cheating with printed photos—motion analysis (Farneback optical flow) checks if the person’s actually there.
- **Attendance Management:** Runs everything through SQLite. Each student gets counted once. Handles late arrivals smoothly.
- **Reports & Analytics:** Exports daily CSV, summary stats, and even bar charts of attendance.
- **CLI Dashboard:** Enroll students, run attendance, see listings, and generate reports—all from the command line.
- **Automated Testing:** Uses Python’s `unittest` for attendance logic, the database, and face detection.

## Stack

- Python 3
- OpenCV (`opencv-python`, `opencv-contrib-python`)
- `face_recognition` / dlib
- SQLite3
- Matplotlib
- `unittest`

## How the Project Looks

```text
facesys/
│
├── main.py             # CLI entry point
├── config.py           # Config settings
├── requirements.txt
├── README.md
├── statement.md
├── .gitignore
│
├── modules/
│   ├── __init__.py
│   ├── face_detector.py
│   ├── face_encoder.py
│   ├── recognizer.py
│   ├── liveness_detector.py
│   ├── attendance_manager.py
│   ├── report_generator.py
│   └── logger.py
│
├── database/
│   └── schema.sql
│
├── data/
│   ├── enrollment/
│   ├── known_faces/
│   ├── encodings_cache.pkl
│   └── attendance_logs/
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

*Personal enrollment photos and actual attendance reports aren’t in the public repo—they’re created/used locally, and `.gitignore` keeps them out.*

# Install & Set Up

## 1. Clone the Repo

```bash
git clone https://github.com/alcyoneus24/Smart-Face-Recognition-Attendance-System.git
cd Smart-Face-Recognition-Attendance-System
```

## 2. Make a Virtual Environment

### On Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
```

### On Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

*Heads up:* `face_recognition` and dlib need CMake and a C++ compiler. If they’re being difficult, you can stick to OpenCV, but it won’t be as accurate.

## 4. Check the Install

```bash
python main.py list-students
```

If it worked, you’ll see:

```text
No students enrolled yet.
```

# How To Use It

Here’s the flow:

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
Recognize Face
↓
Check Liveness
↓
Mark Attendance
↓
Generate Reports
```

## 1. Enroll a Student

Grab 1–3 clear, straight-on face shots of each student.

Then run:

```bash
python main.py enroll --name "Jane Doe" --roll CS101 --images photo1.jpg photo2.jpg photo3.jpg
```

Or, another example:

```bash
python main.py enroll --name "Aditya Taiwade" --roll 24BAI10147 --images aditya1.jpg aditya2.jpg aditya3.jpg
```

During enrollment, it:

- Stores the photos
- Adds the student to the database
- Detects faces
- Builds face embeddings
- Saves everything locally

You’ll see something like:

```text
Rebuilding face encodings, this may take a moment...
Enrolled 'Jane Doe' with 3 photo(s).
```

**Tips:**

- Get clear, straight-on photos
- Faces should be easy to see
- Avoid dark or blurry pics
- Try for consistent lighting
- 2–3 shots is plenty

## 2. List Who’s Enrolled

```bash
python main.py list-students
```

You’ll get something like:

```text
ID  Name                Roll No        Enrolled On
1   Jane Doe            CS101          2026-09-18
```

## 3. Run Live Attendance

Before you start:

- Plug in your webcam
- Enroll at least one student
- Activate your virtual environment

Then:

```bash
python main.py run
```

A window pops up with live video. It draws bounding boxes, shows names, face distances, and if the person’s “LIVE.”

```text
Jane Doe (0.22) LIVE
```

As soon as the system spots a known, real face, attendance is marked—automatically.

To quit, just hit `q`.

## 4. Get Today’s Attendance Report

After the session:

```bash
python main.py report --today
```

You’ll find the CSV in:

```text
data/attendance_logs/
```

Say, `attendance_2026-09-18.csv`

## 5. See Summary and Chart

```bash
python main.py report --summary
```

You’ll get:

```text
data/attendance_logs/attendance_summary.csv
data/attendance_logs/attendance_chart.png
```

The summary lists each student, days present, and attendance percentage.

## 6. Run the Tests

You can run all the basic tests with:

```bash
python -m unittest discover -s tests -v
```

Covers:

- Enrollment
- Listing students
- Attendance marking
- Duplication checks
- Unknown faces
- Face detection

All green? You’ll see:

```text
Ran 9 tests

OK
```

Test data is used, so your real records stay safe.

# Step-by-Step: Full Example

Fresh install? Here’s what to do:

1. Clone the repo
2. Set up and activate your virtual environment
3. Install requirements
4. Enroll a student (with 1–3 photos)
5. Check enrollment
6. Start attendance (live webcam)
7. Generate today’s report
8. Generate summary and chart
9. Run all tests

# Attendance Rules

Attendance is marked only when:

- A face is detected
- It matches a registered student
- The liveness check passes

Multiple entries won’t slip in, and late arrivals are handled.

# Troubleshooting

**Webcam Not Working?**

- Is it plugged in?
- Another app using it?
- Python got camera permissions?

Error:

```text
ERROR: could not access the webcam.
```

**No Face Recognized?**

- Turn up the lights
- Use better enrollment photos
- Face the camera straight on
- Try re-enrolling using new photos

**Already Marked Present?**  
That’s on purpose—duplicates aren’t allowed.

**Install Issues?**  
If dlib or `face_recognition` won’t install, make sure CMake and a C++ compiler are installed. Worst case, you can fall back to the basic encoder (but accuracy drops).

# Project Documentation

You get:

- Architecture diagram
- Use case diagram
- Workflow diagram
- Sequence diagram
- Class diagram
- ER diagram

All are in:

```text
docs/diagrams/
```

The main project statement is in:

```text
statement.md
```

# What We Tested

On live webcam, the project demonstrated:

- Real-time face detection
- Recognition
- Liveness—no proxy cheating
- Auto-marking of attendance
- No duplicates
- CSV report export
- Summaries and attendance charts
- Automated unit tests all passing

# Privacy & Data

No personal data lives in the public repo.

Locally, the system keeps:

- Enrollment photos
- Known faces
- Encodings
- The attendance DB
- CSV reports
- Attendance charts
- Logs

Only use photos you’re allowed to.

# Where Next?

Some ideas for upgrades:

- Switch to DNN-based detection (like SSD or RetinaFace) for better results—especially if faces aren’t front and center or the lighting is tricky.
- A better liveness detector (eye-blink detection, maybe?) instead of just watching for motion.
- A web dashboard (Flask, Streamlit).
- Support more cameras—bigger classrooms—track faces over time.
- Make it work better under weird lighting.
- Add admin roles and authentication.

# Academic Project Info

Done for:

**CSE3010 – Computer Vision**  
**VIT Bhopal**  
**VITyarthi – Build Your Own Project**