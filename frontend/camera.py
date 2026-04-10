import cv2
import mediapipe as mp
import numpy as np

class PushUpDetector(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        # model_complexity=1 is better for tracking the whole body stance
        self.pose = self.mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5)
        
        self.counter = 0
        self.stage = "up"
        self.activity = "Detecting..."
        self.feedback = "Positioning..."

    def __del__(self):
        if self.cap.isOpened(): self.cap.release()

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0: angle = 360-angle
        return angle

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret: return None
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Initialize to prevent crashes
        active_side = "Scanning..."

        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            try:
                landmarks = results.pose_landmarks.landmark
                
                # 1. GET KEY POINTS
                # We use x and y to calculate the "Box" the user is in
                shldr = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
                hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]

                # 2. RATIO-BASED ACTIVITY DETECTION
                # Calculate horizontal length vs vertical height
                horiz_dist = abs(shldr.x - ankle.x)
                vert_dist = abs(shldr.y - ankle.y)

                # In a push-up, Horizontal distance is usually 2x+ the Vertical distance
                if horiz_dist > (vert_dist * 1.2):
                    self.activity = "Push-up Mode"
                else:
                    self.activity = "Sitting/Standing"
                    self.feedback = "Please lie down"

                # 3. PUSH-UP COUNTER (Only if Mode is correct)
                if self.activity == "Push-up Mode":
                    # Determine which side is more visible
                    l_vis = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility
                    r_vis = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility

                    if l_vis > r_vis:
                        shoulder = [shldr.x, shldr.y]
                        elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                        active_side = "Left Side"
                    else:
                        shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                        elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                        wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                        active_side = "Right Side"

                    angle = self.calculate_angle(shoulder, elbow, wrist)

                    # Strict counting logic
                    if angle > 155: # Fully Up
                        if self.stage == "down":
                            self.counter += 1
                            self.feedback = "Good Rep!"
                        self.stage = "up"
                    
                    if angle < 100 and self.stage == "up": # Fully Down
                        self.stage = "down"
                        self.feedback = "Push Back Up!"

            except Exception:
                pass

        # --- UPDATED UI ---
        # Dark header for contrast
        cv2.rectangle(image, (0,0), (320, 110), (15, 15, 15), -1)
        
        # Reps
        cv2.putText(image, f'REPS: {self.counter}', (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Mode with color coding
        mode_color = (0, 255, 255) if self.activity == "Push-up Mode" else (0, 0, 255)
        cv2.putText(image, f'{self.activity}', (15, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)
        
        # Feedback
        cv2.putText(image, f'{self.feedback}', (15, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()