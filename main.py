import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import face_recognition 


# Load known faces and their names
known_face_encodings = []
known_face_names = []


# Path to the known faces folder
known_faces_dir = 'known_faces'


# Load known faces
for filename in os.listdir(known_faces_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(known_faces_dir, filename)
        # Get the name without the extension
        name = os.path.splitext(filename)[0]
        known_face_names.append(name)
        # Load the image
        img = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(img)
        if encoding:
            known_face_encodings.append(encoding[0])
        else:
            print(f"No encoding found for {filename}")

# Initialize variables
process_this_frame = True

# Function to update the frame
def update_frame():
    global process_this_frame

    # Grab a single frame of video
    ret, frame = video_capture.read()
    if not ret:
        return

    # Convert the image from BGR color (which OpenCV uses) to RGB color
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces and encode them
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # Compare faces
        distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(distances)
        if distances[best_match_index] < 0.6:  # Threshold for a match
            name = known_face_names[best_match_index]
        else:
            name = "NOT AUTHORIZED"
            face_names.append(name)

        # Trigger an alarm if an unauthorized person is detected
        if name == "NOT AUTHORIZED":
            root.after(1, lambda: messagebox.showwarning("Unauthorized Access", "ALARM! Unauthorized person detected!"))

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Convert the image to PIL format
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)

    # Update the image in the GUI
    label.imgtk = imgtk
    label.configure(image=imgtk)

    # Repeat after an interval to create a loop
    root.after(2, update_frame)

# Set up the GUI
root = tk.Tk()
root.title("Trespasser Identification System")

# Set up the video capture
video_capture = cv2.VideoCapture(0)

# Create a label to display the video feed
label = tk.Label(root)
label.pack()

# Start the video loop
update_frame()

# Start the GUI loop
root.mainloop()

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
