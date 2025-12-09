# Jackfruit-Problem--Face-Recognition-Attendance-System
Traditional attendance systems in institutions—such as roll calls or signature sheets—are slow, error-prone, and easy to manipulate. They disrupt class time and make it difficult to maintain accurate, reliable records. As a result, managing and analysing attendance data becomes inefficient for both faculty and administration.
# Jackfruit-Problem-Face-Recognition-Attendance-System

##  Project Overview

This is a **Real-time Face Recognition Attendance System** designed to automate the process of tracking attendance using a standard webcam. Built with Python, OpenCV, and Tkinter, it provides a user-friendly GUI for monitoring attendance logs as they happen.

The system is highly effective for classroom, small office, or event entry logging, offering a fast and reliable alternative to manual check-ins.



---

## Key Features

* **Real-time Recognition:** Uses the `face_recognition` library to detect and identify known faces against a database of registered images.
* **Automated CSV Logging:** Creates a new attendance log file (`attendance_YYYY-MM-DD.csv`) every day in the `attendance/` directory.
* **Late Threshold Check:** Automatically calculates and flags the entry status as **"Late"** if the sign-in time is after a configurable threshold (default is 08:15:00).
* **Interactive Tkinter GUI:** Displays the live camera feed, frames faces with bounding boxes (color-coded by status), and updates the attendance log table in real-time.
* **Scalable Face Management:** Easily add new registered faces by dropping images into a dedicated folder.

---

## Prerequisites

Ensure you have the following installed on your system:


* **Python 3.10** (Tested and works with this version)
* **A functional Webcam**
* **Registered_faces** (Folder containing all registered faces)
* **Git** (for cloning the repository)

---

## Mentor

This project was developed under the guidance of:

**AMBIKA K**

Assistant Professor, Department of Computer Science and Engineering, PES University

**Email:** amikak@pes.edu
