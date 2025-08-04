import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Tuple, List
from pose.pose_estimator import PoseEstimator
from analysis.analyzer import ExerciseAnalyzer

def load_video_frames(video_path: str, resize: Tuple[int, int] = (540, 480)) -> List[np.ndarray]:
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame_resized = cv2.resize(frame, resize)
        frames.append(frame_resized)
    cap.release()
    return frames

def load_video_frames(video_path: str, resize: Tuple[int, int] = (540, 480)) -> List[np.ndarray]:
    print(f"Loading video from: {video_path}")  # Add this line
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame_resized = cv2.resize(frame, resize)
        frames.append(frame_resized)
    cap.release()
    print(f"Total frames loaded: {len(frames)}")  # Add this line
    return frames

def main():
    pose_estimator = PoseEstimator(alpha=0.5)
    analyzer = ExerciseAnalyzer()
    
    # Load video
    video_path = 'pose/1.mp4'
    frames = load_video_frames(video_path)

    # Analyze
    results = analyzer.analyze_video(frames, pose_estimator)

    # Show summary
    import json
    print(json.dumps(results["summary"], indent=2))

    # Optional: visualize annotated output
    # for idx, frame in enumerate(frames):
    #     landmarks = pose_estimator.extract_keypoints(frame)
    #     frame_with_pose = pose_estimator.draw_pose(frame, landmarks)
    #     cv2.imshow("Pose", frame_with_pose)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    # cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()
