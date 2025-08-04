import cv2
from pose.pose_estimator import PoseEstimator
from analysis.analyzer import ExerciseAnalyzer

def run_analysis_on_video(video_path: str):
    pose_estimator = PoseEstimator()
    analyzer = ExerciseAnalyzer()
    frames = []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break
        landmarks = pose_estimator.extract_keypoints(frame)
        frames.append(landmarks)

    cap.release()

    result = analyzer.analyze_video(frames)

    print("\n=== ANALYSIS SUMMARY ===")
    print(f"Squats: {result['summary']['squats']['total_reps']} reps "
          f"(Good form: {result['summary']['squats']['good_form_reps']})")
    print("Squat issues:", result['summary']['squats']['common_issues'])
    
    print(f"Pushups: {result['summary']['pushups']['total_reps']} reps "
          f"(Good form: {result['summary']['pushups']['good_form_reps']})")
    print("Pushup issues:", result['summary']['pushups']['common_issues'])

if __name__ == "__main__":
    run_analysis_on_video("pose/push.mp4")  # Change to your actual video path
