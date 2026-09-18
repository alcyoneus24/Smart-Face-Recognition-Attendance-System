"""
face_encoder.py
----------------
Converts a detected face image into a numerical feature vector (embedding)
that can be compared against known faces.

Maps to CSE3010 syllabus:
  Module 3 - Feature Extraction (HOG / deep embeddings) and
  Module 4 - Dimensionality reduction concepts (embeddings are a learned
             128-D reduction of the raw pixel space).

We use the `face_recognition` library (built on dlib's ResNet embedding
model) as the primary encoder because it gives far more robust features
than classical HOG+SVM for a real deployment, and we fall back to an
OpenCV LBPH-based encoder if `face_recognition`/dlib is not installed,
so the system still runs in constrained environments.
"""

import pickle
from typing import List, Optional

import cv2
import numpy as np

import config
from modules.logger import get_logger

log = get_logger(__name__)

try:
    import face_recognition
    _BACKEND = "dlib_resnet"
except ImportError:  # pragma: no cover - fallback path
    face_recognition = None
    _BACKEND = "lbph_fallback"
    log.warning(
        "face_recognition/dlib not available - falling back to a simpler "
        "LBPH-histogram encoder. Install `face_recognition` for production "
        "quality accuracy."
    )


class FaceEncoder:
    """Extracts a fixed-length feature vector for a cropped face image."""

    def __init__(self):
        self.backend = _BACKEND
        if self.backend == "lbph_fallback":
            self.lbph = cv2.face.LBPHFaceRecognizer_create() \
                if hasattr(cv2, "face") else None

    def encode(self, face_bgr: np.ndarray) -> Optional[np.ndarray]:
        """Return a 1-D numpy feature vector for the given face crop."""
        if face_bgr is None or face_bgr.size == 0:
            return None

        if self.backend == "dlib_resnet":
            rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb)
            if not encodings:
                return None
            return encodings[0]

        # ---- Fallback: simple, dependency-free "feature" using a
        # normalised, resized grayscale histogram. Not as discriminative
        # as a learned embedding, but keeps the pipeline functional.
        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (100, 100))
        equalized = cv2.equalizeHist(resized)
        hist = cv2.calcHist([equalized], [0], None, [256], [0, 256])
        return cv2.normalize(hist, hist).flatten()

    @staticmethod
    def compare(known_vec: np.ndarray, candidate_vec: np.ndarray) -> float:
        """
        Returns a distance score - lower means more similar.
        Uses Euclidean distance, matching face_recognition's convention.
        """
        return float(np.linalg.norm(known_vec - candidate_vec))

    # ------------------------------------------------------------------ #
    # Persisting encodings so we don't need to re-encode enrolled faces
    # every time the app starts (Non-functional: performance).
    # ------------------------------------------------------------------ #
    @staticmethod
    def save_cache(encodings: List[np.ndarray], names: List[str], path: str = config.ENCODINGS_CACHE):
        with open(path, "wb") as f:
            pickle.dump({"encodings": encodings, "names": names}, f)
        log.info("Saved %d encodings to cache: %s", len(names), path)

    @staticmethod
    def load_cache(path: str = config.ENCODINGS_CACHE):
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            return data["encodings"], data["names"]
        except FileNotFoundError:
            return [], []
