import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple
import math

class PoseEstimator:
    def __init__(self, alpha=0.5):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,  #  frames in a video stream not just static images
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,  # detection confidence threshold
            min_tracking_confidence=0.5  # tracking confidence threshold
        )
        self.alpha = alpha  # Smoothing factor for EMA
        self.prev_keypoints = None  # To store the previous frame's keypoints for EMA

#keypoints from a single frame"""
    def extract_keypoints(self, frame: np.ndarray) -> Optional[Dict]:
        """Extract pose keypoints from a single frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            landmarks = {}
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                landmark_name = self.mp_pose.PoseLandmark(idx).name
                landmarks[landmark_name] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                }
            # Apply smoothing to the keypoints
            smoothed_landmarks = self.smooth_keypoints(landmarks)
            return smoothed_landmarks
        return None
    
    #Applying Exponential Moving Average (EMA) to smooth the keypoints"""
    def smooth_keypoints(self, keypoints: Dict) -> Dict:
        if self.prev_keypoints is None:
            self.prev_keypoints = keypoints
            return keypoints
        
        smoothed_keypoints = {}
        for landmark_name, current_point in keypoints.items():
            prev_point = self.prev_keypoints.get(landmark_name, current_point)
            smoothed_point = {
                'x': self.alpha * current_point['x'] + (1 - self.alpha) * prev_point['x'],
                'y': self.alpha * current_point['y'] + (1 - self.alpha) * prev_point['y'],
                'z': self.alpha * current_point['z'] + (1 - self.alpha) * prev_point['z']
            }
            smoothed_keypoints[landmark_name] = smoothed_point
        
        # Update the previous keypoints
        self.prev_keypoints = smoothed_keypoints
        return smoothed_keypoints

   # Drawing pose skeleton on frame 
    def draw_pose(self, frame: np.ndarray, landmarks: Dict) -> np.ndarray:
        if landmarks:
            # Convert landmarks back to MediaPipe format for drawing
            landmark_list = []
            for i in range(33):  # MediaPipe has 33 pose landmarks
                landmark_name = self.mp_pose.PoseLandmark(i).name
                if landmark_name in landmarks:
                    lm = landmarks[landmark_name]
                    landmark_list.append([lm['x'], lm['y'], lm['z']])
                else:
                    landmark_list.append([0, 0, 0])
            
            # Draw landmarks and connections
            h, w, _ = frame.shape
            for i, lm in enumerate(landmark_list):
                if lm[0] > 0 and lm[1] > 0:
                    cv2.circle(frame, (int(lm[0] * w), int(lm[1] * h)), 5, (0, 255, 0), -1)
        
        return frame

# Example usage
pose_estimator = PoseEstimator(alpha=0.5)  # Set alpha for smoothing (0.5) after trials is chosen

cap = cv2.VideoCapture('demo/squat.mp4')  

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Failed to capture frame.")
        break

    # Resize the frame (resize to 540x480 or any other size)
    frame_resized = cv2.resize(frame, (540, 480))

    # Extract keypoints from the frame (with smoothing applied)
    landmarks = pose_estimator.extract_keypoints(frame_resized)

    # Draw pose on the frame
    frame_with_pose = pose_estimator.draw_pose(frame_resized, landmarks)

    # Display the frame with pose landmarks
    cv2.imshow("Pose Estimation", frame_with_pose)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()
