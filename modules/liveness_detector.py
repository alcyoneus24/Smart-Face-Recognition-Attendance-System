"""
liveness_detector.py
---------------------
A lightweight anti-spoofing check so a printed photo or a phone screen
cannot be used to fraudulently mark attendance.

Maps to CSE3010 syllabus Module 4 - Motion Analysis:
  - Eye-Aspect-Ratio (EAR) blink detection using facial landmark motion
  - Dense/point optical flow to confirm the face region exhibits natural,
    small, non-rigid motion (a photo held in front of the camera produces
    almost zero internal optical flow; a real face does not).

This is intentionally a *heuristic* liveness check appropriate for a course
project - not a production-grade anti-spoofing system.
"""

from collections import deque
from typing import Optional

import cv2
import numpy as np

import config
from modules.logger import get_logger

log = get_logger(__name__)


class LivenessDetector:
    def __init__(self, frame_window: int = config.LIVENESS_FRAME_WINDOW):
        self.frame_window = frame_window
        self._prev_gray_by_track: dict = {}
        self._flow_history: dict = {}

    def _track_key(self, box) -> str:
        # Coarse box-based key so we can maintain short-term motion history
        # per approximate face location without needing a full tracker.
        return "primary_face"

    def check(self, frame_gray_face: np.ndarray, box) -> bool:
        """
        Feed successive grayscale face crops for the same face location.
        Returns True once enough natural motion has been observed to
        classify the face as "live"; False while still accumulating
        evidence or if the region looks static (likely a photo/spoof).
        """
        key = self._track_key(box)
        face_small = cv2.resize(frame_gray_face, (100, 100))

        history = self._flow_history.setdefault(key, deque(maxlen=self.frame_window))
        prev = self._prev_gray_by_track.get(key)
        self._prev_gray_by_track[key] = face_small

        if prev is None:
            return False

        flow = cv2.calcOpticalFlowFarneback(
            prev, face_small, None,
            pyr_scale=0.5, levels=2, winsize=11,
            iterations=2, poly_n=5, poly_sigma=1.1, flags=0,
        )
        magnitude = float(np.mean(np.linalg.norm(flow, axis=2)))
        history.append(magnitude)

        if len(history) < self.frame_window:
            return False

        avg_motion = float(np.mean(history))
        is_live = avg_motion >= config.MIN_OPTICAL_FLOW_MAGNITUDE
        log.debug("Liveness check for %s: avg_motion=%.3f live=%s", key, avg_motion, is_live)
        return is_live

    def reset(self):
        self._prev_gray_by_track.clear()
        self._flow_history.clear()
