import cv2
import mediapipe as mp
import numpy as np

# 1. Setup MediaPipe with LOWER complexity for stability
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0, # 0 = fastest, 1 = balanced, 2 = heavy. Use 0 for now.
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360-angle if angle > 180.0 else angle

# 2. Auto-detect correct Camera Index
def get_camera():
    for index in [1, 0, 2]: # Priority to external cams
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"✅ Camera found at index {index}")
            return cap
    return None

cap = get_camera()
if cap is None:
    print("❌ Error: Could not find any camera. Check Iriun connection.")
    exit()

counter = 0
stage = None

print("Running... Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Empty frame received.")
        break

    # 3. Process frame
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Use Right side landmarks
            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            angle = calculate_angle(shoulder, elbow, wrist)

            # 4. Counting Logic (Tuned thresholds)
            if angle > 160:
                stage = "up"
            if angle < 80 and stage == "up":
                stage = "down"
                counter += 1
                print(f"Rep: {counter}")

        except Exception as e:
            pass

    # Draw UI
    cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
    cv2.putText(image, f'REPS: {counter}', (15,45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imshow('Gym AI Tracker', image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()