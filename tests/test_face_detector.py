"""
test_face_detector.py
Sanity tests for the FaceDetector's image preprocessing and detection API
using synthetic images (no external test images required to run CI).
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.face_detector import FaceDetector  # noqa: E402


class TestFaceDetector(unittest.TestCase):
    def setUp(self):
        self.detector = FaceDetector()

    def test_preprocess_output_shape_and_type(self):
        frame = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        processed = self.detector.preprocess(frame)
        self.assertEqual(processed.shape, (200, 200))
        self.assertEqual(processed.dtype, np.uint8)

    def test_detect_on_blank_frame_returns_no_faces(self):
        blank = np.zeros((300, 300, 3), dtype=np.uint8)
        faces = self.detector.detect(blank)
        self.assertEqual(faces, [])

    def test_detect_returns_list(self):
        random_frame = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        faces = self.detector.detect(random_frame)
        self.assertIsInstance(faces, list)


if __name__ == "__main__":
    unittest.main()
