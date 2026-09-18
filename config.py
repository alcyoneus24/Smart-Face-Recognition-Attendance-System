"""
config.py
Centralised configuration for the Smart Face Recognition Attendance System.
Keeping all tunables in one place satisfies the 'maintainability' and
'configurability' non-functional requirements.
"""

import os

# ---------------------------------------------------------------- Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "data", "known_faces")
ATTENDANCE_LOG_DIR = os.path.join(BASE_DIR, "data", "attendance_logs")
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")
ENCODINGS_CACHE = os.path.join(BASE_DIR, "data", "encodings_cache.pkl")

# ---------------------------------------------------------- Detection / Recognition
# Haar cascade is used for fast, dependency-light face *detection*.
HAAR_CASCADE_PATH = "haarcascade_frontalface_default.xml"

# Recognition tolerance: lower = stricter match (face_recognition uses
# Euclidean distance between 128-d embeddings).
RECOGNITION_TOLERANCE = 0.5

# Minimum face size (pixels) to be considered a valid detection - filters
# out noise / far-away background faces.
MIN_FACE_SIZE = (60, 60)

# ---------------------------------------------------------- Liveness (anti-spoofing)
# Number of consecutive frames used to measure eye-aspect-ratio blinking
# and optical-flow motion before a face is accepted as "live".
LIVENESS_FRAME_WINDOW = 8
EAR_BLINK_THRESHOLD = 0.21
MIN_OPTICAL_FLOW_MAGNITUDE = 0.2

# ---------------------------------------------------------- Performance
FRAME_RESIZE_SCALE = 0.5   # downscale frames before detection for speed
PROCESS_EVERY_N_FRAMES = 3 # skip frames to hit real-time targets on CPU
RECOGNITION_EVERY_N_FRAMES = 3  

# ---------------------------------------------------------- Attendance rules
MIN_MINUTES_BETWEEN_MARKS = 5   # avoid duplicate marks for the same person
WORK_START_TIME = "09:00"
LATE_AFTER_TIME = "09:15"

# ---------------------------------------------------------- Logging
LOG_FILE = os.path.join(BASE_DIR, "system.log")
LOG_LEVEL = "INFO"
