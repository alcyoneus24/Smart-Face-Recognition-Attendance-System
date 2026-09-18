"""
recognizer.py
-------------
Given a face encoding, finds the closest match among enrolled students.

Maps to CSE3010 syllabus Module 4 - Pattern Analysis / Classification:
this is effectively a 1-Nearest-Neighbour classifier over face embeddings.
"""

import os
from typing import List, Optional, Tuple

import cv2
import numpy as np

import config
from modules.face_detector import FaceDetector
from modules.face_encoder import FaceEncoder
from modules.logger import get_logger

log = get_logger(__name__)


class Recognizer:
    def __init__(self):
        self.detector = FaceDetector()
        self.encoder = FaceEncoder()
        self.known_encodings: List[np.ndarray] = []
        self.known_names: List[str] = []
        self._load_known_faces()

    # ------------------------------------------------------------------ #
    def _load_known_faces(self):
        """Load cached encodings, or build them from the enrolled-image
        folder if the cache is missing/out of date."""
        self.known_encodings, self.known_names = self.encoder.load_cache()
        if self.known_encodings:
            log.info("Loaded %d cached face encodings.", len(self.known_names))
            return

        self.rebuild_encodings()

    def rebuild_encodings(self):
        """(Re)compute encodings for every image under data/known_faces/<name>/*.jpg"""
        encodings, names = [], []
        if not os.path.isdir(config.KNOWN_FACES_DIR):
            os.makedirs(config.KNOWN_FACES_DIR, exist_ok=True)

        for person_name in sorted(os.listdir(config.KNOWN_FACES_DIR)):
            person_dir = os.path.join(config.KNOWN_FACES_DIR, person_name)
            if not os.path.isdir(person_dir):
                continue
            for img_name in os.listdir(person_dir):
                img_path = os.path.join(person_dir, img_name)
                image = cv2.imread(img_path)
                if image is None:
                    log.warning("Could not read enrollment image: %s", img_path)
                    continue
                faces = self.detector.detect(image)
                if not faces:
                    log.warning("No face found in enrollment image: %s", img_path)
                    continue
                vec = self.encoder.encode(faces[0].aligned_face)
                if vec is not None:
                    encodings.append(vec)
                    names.append(person_name)

        self.known_encodings, self.known_names = encodings, names
        self.encoder.save_cache(encodings, names)
        log.info("Rebuilt encodings for %d enrolled samples.", len(names))

    # ------------------------------------------------------------------ #
    def identify(self, face_vec: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Compare a candidate face vector against all known encodings.
        Returns (name, distance) or (None, inf) if nobody is close enough.
        """
        if not self.known_encodings:
            return None, float("inf")

        distances = [self.encoder.compare(k, face_vec) for k in self.known_encodings]
        best_idx = int(np.argmin(distances))
        best_distance = distances[best_idx]

        if best_distance <= config.RECOGNITION_TOLERANCE:
            return self.known_names[best_idx], best_distance
        return None, best_distance
