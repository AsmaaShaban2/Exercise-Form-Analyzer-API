from pose.pose_estimator import PoseEstimator
import numpy as np

def test_smoothing_keypoints():
    pose = PoseEstimator(alpha=0.5)
    fake_landmarks = {
        "LEFT_SHOULDER": {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0}
    }

    smoothed = pose.smooth_keypoints(fake_landmarks)
    assert smoothed["LEFT_SHOULDER"]["x"] == 0.5

    # Simulate next frame with a slight movement
    new_landmarks = {
        "LEFT_SHOULDER": {"x": 0.7, "y": 0.5, "z": 0.0, "visibility": 1.0}
    }

    smoothed = pose.smooth_keypoints(new_landmarks)
    # Expected: x = 0.5*0.7 + 0.5*0.5 = 0.6
    assert round(smoothed["LEFT_SHOULDER"]["x"], 2) == 0.6
