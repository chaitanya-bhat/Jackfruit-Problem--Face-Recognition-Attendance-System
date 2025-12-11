import os
import cv2
import csv
from datetime import datetime, time
import face_recognition
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ---------------------------
# SETTINGS
# ---------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REGISTERED_FOLDER = os.path.join(BASE_DIR, "registered_faces")
ATTENDANCE_FOLDER = os.path.join(BASE_DIR, "attendance")

DETECTION_MODEL = "hog"
DOWNSCALE_SIZE = 0.5
TOLERANCE = 0.45
UPDATE_DELAY = 10

LATE_THRESHOLD_TIME = time(8, 15, 0)

CAMERA_WIDTH = 850
CAMERA_HEIGHT = 650

# ---------------------------
# DAILY ATTENDANCE FILE & MARKING
# ---------------------------
def get_today_file():
    today = datetime.now().strftime("%Y-%m-%d")
    file = os.path.join(ATTENDANCE_FOLDER, f"attendance_{today}.csv")

    if not os.path.exists(ATTENDANCE_FOLDER):
        try:
            os.makedirs(ATTENDANCE_FOLDER)
        except OSError as e:
            print(f"Error creating attendance directory: {e}")
            raise

    if not os.path.exists(file):
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Time", "Status"])

    return file

# Initialize file and set
try:
    ATTENDANCE_FILE = get_today_file()
    marked_today = set()
except Exception as e:
    print(f"Fatal error during file initialization: {e}")
    exit()


def mark_attendance(name):
    if name in marked_today:
        return

    now = datetime.now()
    time_now_str = now.strftime("%H:%M:%S")
    
    if now.time() > LATE_THRESHOLD_TIME:
        status = "Late"
        tag = "Late"
    else:
        status = "Present"
        tag = "Present"

    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, time_now_str, status])

    attendance_table.insert("", "end", values=(name, time_now_str, status), tags=(tag,))

    marked_today.add(name)


# ---------------------------
# LOAD REGISTERED FACES
# ---------------------------
known_encodings = []
known_names = []

print("Loading registered faces...")
for file in os.listdir(REGISTERED_FOLDER):
    path = os.path.join(REGISTERED_FOLDER, file)
    name, ext = os.path.splitext(file)

    if ext.lower() not in [".jpg", ".jpeg", ".png"]:
        continue

    try:
        img = face_recognition.load_image_file(path)
        enc = face_recognition.face_encodings(img)

        if len(enc) > 0:
            known_encodings.append(enc[0])
            known_names.append(name)
            print(f"Loaded: {name}")
        else:
            print(f"No face found in {file}")
    except Exception as e:
        print(f"Error loading or processing image {file}: {e}")

print(f"Total registered faces: {len(known_names)}")


# ---------------------------
# TKINTER GUI
# ---------------------------
window = tk.Tk()
window.title("Face Recognition Attendance System")
window.geometry("1400x750") 
window.configure(bg="#2c3e50")

style = ttk.Style()
style.theme_use('clam') 

style.configure('TFrame', background='#2c3e50')
style.configure('TLabel', background='#2c3e50', foreground='white', font=('Helvetica', 12))
style.configure('TNotebook', background='#34495e')

style.configure("Treeview", 
    background="#34495e", 
    foreground="white",
    rowheight=25,
    fieldbackground="#34495e",
    font=('Helvetica', 10)
)
style.map('Treeview', background=[('selected', '#4e5a65')]) 
style.configure("Treeview.Heading", 
    font=('Helvetica', 12, 'bold'), 
    background='#1e2a38', 
    foreground='white'
)

main_frame = ttk.Frame(window, padding="15 15 15 15")
main_frame.pack(fill="both", expand=True)

camera_frame = ttk.Frame(main_frame, relief="raised", padding="10")
camera_frame.pack(side="left", padx=15, pady=15, fill="both", expand=True)

ttk.Label(camera_frame, text=" Live Camera Feed ", font=("Helvetica", 16, "bold"), 
          foreground="#3498db", anchor="center").pack(pady=5)

camera_label = tk.Label(camera_frame, bg="black", width=CAMERA_WIDTH, height=CAMERA_HEIGHT) 
camera_label.pack(fill="both", expand=True)

threshold_text = f"Class starts: 8:00 AM | Late after: {LATE_THRESHOLD_TIME.strftime('%H:%M:%S')}"
ttk.Label(camera_frame, text=threshold_text, font=("Helvetica", 12, "bold"), foreground="#e74c3c").pack(pady=5)

info_label = ttk.Label(camera_frame, font=("Helvetica", 14, 'italic'), foreground="#2ecc71")
info_label.pack(pady=10)

table_frame = ttk.Frame(main_frame, relief="raised", padding="10")
table_frame.pack(side="right", padx=15, pady=15, fill="y")

ttk.Label(table_frame, text=" Today's Attendance Log ", font=("Helvetica", 16, "bold"), 
          foreground="#f1c40f").pack(pady=10)

attendance_table = ttk.Treeview(
    table_frame,
    columns=("Name", "Time", "Status"),
    show="headings",
    height=30
)
attendance_table.heading("Name", text="Name", anchor="w")
attendance_table.heading("Time", text="Time", anchor="w")
attendance_table.heading("Status", text="Status", anchor="center")

attendance_table.column("Name", width=160, anchor="w")
attendance_table.column("Time", width=120, anchor="w")
attendance_table.column("Status", width=100, anchor="center")

attendance_table.tag_configure('Late', background='#f39c12', foreground='black')
attendance_table.tag_configure('Present', background='#16a085', foreground='white')

attendance_table.pack()

# Load today's attendance from CSV
if os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, "r") as f:
        reader = csv.reader(f)
        try:
            next(reader)
        except StopIteration:
            pass
        for row in reader:
            if len(row) >= 3:
                name, time_str, status = row
                
                tag = "Late" if status == "Late" else "Present"
                
                attendance_table.insert("", "end", values=(name, time_str, status), tags=(tag,))
                marked_today.add(name)
            
            elif len(row) == 2:
                name, time_str = row
                status = "Present"
                tag = "Present"
                attendance_table.insert("", "end", values=(name, time_str, status), tags=(tag,))
                marked_today.add(name)


# ---------------------------
# CAMERA + FACE RECOGNITION LOOP
# ---------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    camera_label.config(text="Camera Error: Check Connection", font=('Helvetica', 18, 'bold'), fg='red')


def update_frame():
    ret, frame = cap.read()
    if not ret:
        window.after(UPDATE_DELAY, update_frame)
        return

    small = cv2.resize(frame, (0, 0), fx=DOWNSCALE_SIZE, fy=DOWNSCALE_SIZE)
    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small, model=DETECTION_MODEL)
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    names_found = []

    for enc in face_encodings:
        name = "Unknown"
        
        if known_encodings:
            face_distances = face_recognition.face_distance(known_encodings, enc)
            best_match_index = np.argmin(face_distances)
            
            if face_distances[best_match_index] < TOLERANCE:
                name = known_names[best_match_index]
                mark_attendance(name)

        names_found.append(name)

    for (top, right, bottom, left), name in zip(face_locations, names_found):
        top = int(top / DOWNSCALE_SIZE)
        right = int(right / DOWNSCALE_SIZE)
        bottom = int(bottom / DOWNSCALE_SIZE)
        left = int(left / DOWNSCALE_SIZE)

        color = (0, 255, 0)
        if name == "Unknown":
            color = (0, 0, 255)
        elif name in marked_today:
            color = (255, 165, 0)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), color, -1)
        cv2.putText(frame, name, (left + 5, bottom - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img_rgb)
    
    max_w = camera_label.winfo_width() 
    max_h = camera_label.winfo_height() 
    
    if max_w > 1 and max_h > 1:
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    
    img_tk = ImageTk.PhotoImage(image=img)

    camera_label.imgtk = img_tk
    camera_label.configure(image=img_tk)

    info_label.config(text=f"Detected: {', '.join(names_found)}" if names_found else "No face detected")

    window.after(UPDATE_DELAY, update_frame)


# Start the main loop
try:
    if cap.isOpened():
        update_frame()
    window.mainloop()
except Exception as e:
    print(f"An error occurred in the main loop: {e}")
finally:
    if 'cap' in locals() and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
