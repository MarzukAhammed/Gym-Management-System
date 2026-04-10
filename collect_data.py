import cv2
import mediapipe as mp
import numpy as np
import csv

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- CONFIGURATION ---
# IMPORTANT: Change this label to "up", "down", or "sitting" before running
class_name = "up" 
# ---------------------

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        try:
            # Extract all 33 landmarks (x, y, z, visibility)
            pose_row = list(np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]).flatten())
            pose_row.insert(0, class_name) # Add label at the start

            # Export to CSV
            with open('pushup_dataset.csv', mode='a', newline='') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(pose_row)
        except Exception as e:
            print(e)

    cv2.putText(image, f'RECORDING: {class_name}', (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.imshow('AI Training - Data Collection', image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()