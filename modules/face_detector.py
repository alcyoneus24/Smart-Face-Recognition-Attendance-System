"""
face_detector.py
-----------------
Handles low-level image processing and face detection.

Maps to CSE3010 syllabus:
  Module 1 - Digital Image Formation & Low-Level Processing
             (histogram equalisation, noise filtering)
  Module 3 - Feature Extraction & Image Segmentation
             (Haar-cascade / DNN based face detection)

This module deliberately keeps detection separate from recognition so the
detector could be swapped (e.g. Haar -> DNN -> MTCNN) without touching the
rest of the pipeline (Non-functional requirement: maintainability).
"""

from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np

import config
from modules.logger import get_logger

log = get_logger(__name__)


@dataclass
class DetectedFace:
    """Simple value object describing one detected face in a frame."""
    box: Tuple[int, int, int, int]   # (x, y, w, h) in the ORIGINAL frame
    aligned_face: np.ndarray         # cropped, preprocessed face (BGR)


class FaceDetector:
    """Wraps OpenCV's Haar-cascade detector with preprocessing steps."""

    def __init__(self, cascade_path: str = config.HAAR_CASCADE_PATH):
        cascade_file = cv2.data.haarcascades + cascade_path
        self.cascade = cv2.CascadeClassifier(cascade_file)
        if self.cascade.empty():
            raise RuntimeError(f"Could not load Haar cascade at {cascade_file}")
        log.info("FaceDetector initialised with cascade: %s", cascade_file)

    # ------------------------------------------------------------------ #
    # Low-level preprocessing (Module 1 concepts)
    # ------------------------------------------------------------------ #
    @staticmethod
    def preprocess(frame: np.ndarray) -> np.ndarray:
        """
        Apply grayscale conversion, Gaussian filtering (denoising) and
        histogram equalisation to improve detection robustness under
        varying illumination.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        equalized = cv2.equalizeHist(denoised)
        return equalized

    # ------------------------------------------------------------------ #
    # Detection (Module 3 concepts)
    # ------------------------------------------------------------------ #
    def detect(self, frame: np.ndarray) -> List[DetectedFace]:
        """
        Detect all faces in a BGR frame.
        Returns a list of DetectedFace objects with bounding boxes mapped
        back to the ORIGINAL (unscaled) frame coordinates.
        """
        small = cv2.resize(
            frame, (0, 0),
            fx=config.FRAME_RESIZE_SCALE, fy=config.FRAME_RESIZE_SCALE
        )
        processed = self.preprocess(small)

        rects = self.cascade.detectMultiScale(
            processed,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=config.MIN_FACE_SIZE,
        )

        scale = 1.0 / config.FRAME_RESIZE_SCALE
        results = []
        for (x, y, w, h) in rects:
            ox, oy, ow, oh = int(x * scale), int(y * scale), int(w * scale), int(h * scale)
            face_crop = frame[max(0, oy):oy + oh, max(0, ox):ox + ow]
            if face_crop.size == 0:
                continue
            results.append(DetectedFace(box=(ox, oy, ow, oh), aligned_face=face_crop))

        return results
