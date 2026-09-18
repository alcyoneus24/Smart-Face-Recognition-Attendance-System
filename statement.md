# Project Statement

## Problem Statement

Manual attendance-taking in classrooms and workplaces is time-consuming,
disruptive to lecture time, and vulnerable to proxy attendance (one
student answering for another). RFID or biometric fingerprint systems
solve the proxy problem but require dedicated hardware at every entry
point and still need students to actively "check in." There is a need for
a **contactless, automated attendance system** that identifies people
passively from a standard camera feed while resisting simple spoofing
attempts such as holding up a photo.

## Scope of the Project

This project implements a desktop computer-vision pipeline that:

1. Enrolls students from a small set of reference photographs.
2. Continuously detects and recognises faces from a live webcam feed.
3. Verifies that a recognised face belongs to a live person (not a
   photo/screen) using motion analysis before marking attendance.
4. Persists attendance records with timestamps and a "late" flag, using
   business rules such as one mark per person per day.
5. Provides analytics and CSV exports for review by staff.

The scope is deliberately limited to a **single-camera, controlled-lighting
classroom scenario** (not multi-camera or crowd-scale surveillance), which
keeps the project achievable within the course timeline while still
covering image formation, feature extraction, pattern classification, and
motion-analysis concepts from the CSE3010 syllabus.

## Target Users

- **Faculty / Administrators** — enroll students, run attendance sessions,
  and review daily/summary attendance reports.
- **Students** — passively attend by being in view of the camera; no
  manual check-in action is required.

## High-Level Features

- Real-time face detection with illumination-robust preprocessing.
- Deep-embedding based face recognition (with a lightweight fallback).
- Optical-flow based liveness / anti-spoofing check.
- SQLite-backed attendance database with duplicate/late-arrival handling.
- CSV and chart-based analytics reporting.
- CLI tooling for enrollment, live sessions, and reports.
- Unit-tested core logic (database rules + detection pipeline).
