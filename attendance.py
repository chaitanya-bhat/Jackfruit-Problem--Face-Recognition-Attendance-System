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
# !!! IMPORTANT: Update these paths if they are not correct for your system !!!
REGISTERED_FOLDER = "C:\\Users\\chait\\Python mini project\\images"
ATTENDANCE_FOLDER = "C:\\Users\\chait\\Python mini project\\logs"
print("Using folder:", REGISTERED_FOLDER)
print("Files:", os.listdir(REGISTERED_FOLDER))


DETECTION_MODEL = "hog"
DOWNSCALE_SIZE = 0.5
TOLERANCE = 0.45
UPDATE_DELAY = 10

# New Threshold Setting
LATE_THRESHOLD_TIME = time(8, 15, 0) # time(hour, minute, second)

# FIX FOR EXPANDING VIDEO SIZE: Set a stable, large initial size for the video container
CAMERA_WIDTH = 850
CAMERA_HEIGHT = 650

# ---------------------------
# DAILY ATTENDANCE FILE & MARKING
# ---------------------------
def get_today_file():
    """Returns the path to today's attendance CSV file, ensuring folders and headers exist."""
    today = datetime.now().strftime("%Y-%m-%d")
    file = os.path.join(ATTENDANCE_FOLDER, f"attendance_{today}.csv")

    # Ensure the attendance directory exists
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
    """Marks attendance, determines 'Late' status, and updates CSV/GUI."""
    if name in marked_today:
        return

    now = datetime.now()
    time_now_str = now.strftime("%H:%M:%S")
    
    # Determine Status
    if now.time() > LATE_THRESHOLD_TIME:
        status = "Late"
        # Style tag for GUI
        tag = "Late"
    else:
        status = "Present"
        # Style tag for GUI
        tag = "Present"

    # Write to CSV file
    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, time_now_str, status])

    # Update GUI Table, applying a tag for coloring
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
# Window size adjusted to accommodate the new camera label size
window.geometry("1400x750") 
window.configure(bg="#2c3e50") # Dark background for modern look

# Apply a style theme
style = ttk.Style()
style.theme_use('clam') 

# Define styles for the overall application
style.configure('TFrame', background='#2c3e50')
style.configure('TLabel', background='#2c3e50', foreground='white', font=('Helvetica', 12))
style.configure('TNotebook', background='#34495e')

# Style for the Treeview (Table)
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

# Main frame (horizontal layout)
main_frame = ttk.Frame(window, padding="15 15 15 15")
main_frame.pack(fill="both", expand=True)

# Left side – Camera Feed and Info
camera_frame = ttk.Frame(main_frame, relief="raised", padding="10")
camera_frame.pack(side="left", padx=15, pady=15, fill="both", expand=True)

# Header for Camera Frame
ttk.Label(camera_frame, text=" Live Camera Feed ", font=("Helvetica", 16, "bold"), 
          foreground="#3498db", anchor="center").pack(pady=5)

# FIX: Set explicit width and height to prevent continuous expansion
camera_label = tk.Label(camera_frame, bg="black", width=CAMERA_WIDTH, height=CAMERA_HEIGHT) 
camera_label.pack(fill="both", expand=True)

# Late Threshold Info
threshold_text = f"Class starts: 8:00 AM | Late after: {LATE_THRESHOLD_TIME.strftime('%H:%M:%S')}"
ttk.Label(camera_frame, text=threshold_text, font=("Helvetica", 12, "bold"), foreground="#e74c3c").pack(pady=5)

info_label = ttk.Label(camera_frame, font=("Helvetica", 14, 'italic'), foreground="#2ecc71")
info_label.pack(pady=10)

# Right side – Attendance Table
table_frame = ttk.Frame(main_frame, relief="raised", padding="10")
table_frame.pack(side="right", padx=15, pady=15, fill="y")

# Header for Table Frame
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

# Define row colors based on status (tags)
attendance_table.tag_configure('Late', background='#f39c12', foreground='black')
attendance_table.tag_configure('Present', background='#16a085', foreground='white')

attendance_table.pack()

# Load today's attendance from CSV
if os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, "r") as f:
        reader = csv.reader(f)
        try:
            next(reader) # Skip header
        except StopIteration:
            pass # File is empty
        for row in reader:
            if len(row) >= 3:
                name, time_str, status = row
                
                # Apply tag for styling when loading existing data
                tag = "Late" if status == "Late" else "Present"
                
                # FIX: Used time_str (local variable) instead of time_now_str (was undefined here)
                attendance_table.insert("", "end", values=(name, time_str, status), tags=(tag,))
                marked_today.add(name)
            
            elif len(row) == 2:
                name, time_str = row
                status = "Present"
                tag = "Present"
                # FIX: Used time_str (local variable) instead of time_now_str
                attendance_table.insert("", "end", values=(name, time_str, status), tags=(tag,))
                marked_today.add(name)


# ---------------------------
# CAMERA + FACE RECOGNITION LOOP
# ---------------------------
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    camera_label.config(text="Camera Error: Check Connection", font=('Helvetica', 18, 'bold'), fg='red')


def update_frame():
    """The main loop for camera feed processing and face recognition."""
    ret, frame = cap.read()
    if not ret:
        window.after(UPDATE_DELAY, update_frame)
        return

    # Resize and convert to RGB for face_recognition
    small = cv2.resize(frame, (0, 0), fx=DOWNSCALE_SIZE, fy=DOWNSCALE_SIZE)
    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    # Find all faces and face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small, model=DETECTION_MODEL)
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    names_found = []

    for enc in face_encodings:
        name = "Unknown"
        
        if known_encodings: # Only compare if we actually loaded faces
            face_distances = face_recognition.face_distance(known_encodings, enc)
            best_match_index = np.argmin(face_distances)
            
            if face_distances[best_match_index] < TOLERANCE:
                name = known_names[best_match_index]
                mark_attendance(name)

        names_found.append(name)

    # Draw boxes and names on the original frame
    for (top, right, bottom, left), name in zip(face_locations, names_found):
        # Scale back the coordinates to the original frame size
        top = int(top / DOWNSCALE_SIZE)
        right = int(right / DOWNSCALE_SIZE)
        bottom = int(bottom / DOWNSCALE_SIZE)
        left = int(left / DOWNSCALE_SIZE)

        color = (0, 255, 0) # Green for Recognized/Present
        if name == "Unknown":
            color = (0, 0, 255) # Red for Unknown
        elif name in marked_today:
            color = (255, 165, 0) # Orange for already marked (to avoid re-marking)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), color, -1)
        cv2.putText(frame, name, (left + 5, bottom - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Convert the OpenCV BGR frame to a PIL Image, then to a Tkinter PhotoImage
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img_rgb)
    
    # Use the fixed size (CAMERA_WIDTH, CAMERA_HEIGHT) set on the label
    max_w = camera_label.winfo_width() 
    max_h = camera_label.winfo_height() 
    
    # Scale image to fit the label size while maintaining aspect ratio
    if max_w > 1 and max_h > 1:
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    
    img_tk = ImageTk.PhotoImage(image=img)

    camera_label.imgtk = img_tk
    camera_label.configure(image=img_tk)

    info_label.config(text=f"Detected: {', '.join(names_found)}" if names_found else "No face detected")

    # Schedule the next frame update
    window.after(UPDATE_DELAY, update_frame)


# Start the main loop
try:
    if cap.isOpened():
        update_frame()
    window.mainloop()
except Exception as e:
    print(f"An error occurred in the main loop: {e}")
finally:
    # Cleanup on exit
    if 'cap' in locals() and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
