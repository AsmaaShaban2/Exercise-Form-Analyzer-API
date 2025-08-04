# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import cv2
# import mediapipe as mp
# import numpy as np
# from typing import Dict, Tuple, List, Optional
# from pose.pose_estimator import PoseEstimator




# class ExerciseAnalyzer:
#     def __init__(self):
#         self.reset()

#     def reset(self):
#         self.squat_state = "up"
#         self.pushup_state = "up"
#         self.rep_id_counter = {"squat": 0, "pushup": 0}
#         self.results = {
#             "summary": {
#                 "squats": {"total_reps": 0, "good_form_reps": 0, "common_issues": []},
#                 "pushups": {"total_reps": 0, "good_form_reps": 0, "common_issues": []}
#             },
#             "frame_data": []
#         }

#     def analyze_video(self, frames: List[np.ndarray], pose_estimator) -> Dict:
#         self.reset()
#         for idx, frame in enumerate(frames):
#             landmarks = pose_estimator.extract_keypoints(frame)
#             if landmarks:
#                 self._analyze_squat(idx, landmarks)
#                 self._analyze_pushup(idx, landmarks)
#         return self.results

#     def _analyze_squat(self, frame_idx: int, lm: Dict):
#         try:
#             hip = self._get_point(lm, "LEFT_HIP")
#             knee = self._get_point(lm, "LEFT_KNEE")
#             ankle = self._get_point(lm, "LEFT_ANKLE")

#             angle = self._calculate_angle(hip, knee, ankle)

#             if self.squat_state == "up" and angle < 100:
#                 self.squat_state = "down"
#             elif self.squat_state == "down" and angle > 160:
#                 self.squat_state = "up"
#                 self.rep_id_counter["squat"] += 1
#                 is_form_ok, issues = self._check_squat_form(lm, angle)
#                 self._log_frame(frame_idx, "squat", self.rep_id_counter["squat"], is_form_ok, {"knee": angle}, issues)
#         except KeyError:
#             pass

#     def _check_squat_form(self, lm: Dict, angle: float) -> Tuple[bool, List[str]]:
#         issues = []
#         if angle > 100:
#             issues.append("INSUFFICIENT_DEPTH")
#         if abs(lm["LEFT_KNEE"]["x"] - lm["LEFT_ANKLE"]["x"]) > 0.2:
#             issues.append("KNEE_OVER_TOE")
#         is_form_ok = not issues
#         self.results["summary"]["squats"]["total_reps"] += 1
#         if is_form_ok:
#             self.results["summary"]["squats"]["good_form_reps"] += 1
#         else:
#             self.results["summary"]["squats"]["common_issues"].extend(issues)
#         return is_form_ok, issues

#     def _analyze_pushup(self, frame_idx: int, lm: Dict):
#         try:
#             shoulder = self._get_point(lm, "LEFT_SHOULDER")
#             elbow = self._get_point(lm, "LEFT_ELBOW")
#             wrist = self._get_point(lm, "LEFT_WRIST")
#             hip = self._get_point(lm, "LEFT_HIP")
#             ankle = self._get_point(lm, "LEFT_ANKLE")

#             angle = self._calculate_angle(shoulder, elbow, wrist)

#             if self.pushup_state == "up" and angle < 90:
#                 self.pushup_state = "down"
#             elif self.pushup_state == "down" and angle > 160:
#                 self.pushup_state = "up"
#                 self.rep_id_counter["pushup"] += 1
#                 is_form_ok, issues = self._check_pushup_form(shoulder, hip, ankle, angle)
#                 self._log_frame(frame_idx, "pushup", self.rep_id_counter["pushup"], is_form_ok, {"elbow": angle}, issues)
#         except KeyError:
#             pass

#     def _check_pushup_form(self, shoulder, hip, ankle, angle) -> Tuple[bool, List[str]]:
#         issues = []
#         vec1 = np.array(hip) - np.array(shoulder)
#         vec2 = np.array(ankle) - np.array(hip)
#         angle_between = self._angle_between_vectors(vec1, vec2)
#         if abs(angle_between - 180) > 15:
#             issues.append("BODY_LINE_BREAK")
#         if angle < 60:
#             issues.append("ELBOW_FLARE")
#         is_form_ok = not issues
#         self.results["summary"]["pushups"]["total_reps"] += 1
#         if is_form_ok:
#             self.results["summary"]["pushups"]["good_form_reps"] += 1
#         else:
#             self.results["summary"]["pushups"]["common_issues"].extend(issues)
#         return is_form_ok, issues

#     def _log_frame(self, frame_idx, exercise, rep_id, is_form_ok, angles, issues):
#         self.results["frame_data"].append({
#             "frame_index": frame_idx,
#             "exercise": exercise,
#             "rep_id": rep_id,
#             "is_form_ok": is_form_ok,
#             "angles": angles,
#             "issues": issues
#         })

#     def _get_point(self, lm: Dict, name: str) -> List[float]:
#         p = lm[name]
#         return [p['x'], p['y']]

#     def _calculate_angle(self, a, b, c) -> float:
#         a, b, c = np.array(a), np.array(b), np.array(c)
#         ba, bc = a - b, c - b
#         cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
#         return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

#     def _angle_between_vectors(self, v1, v2) -> float:
#         cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
#         return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

# # # Main test
# # if __name__ == "__main__":
# #     pose_estimator = PoseEstimator(alpha=0.5)
# #     analyzer = ExerciseAnalyzer()
# #     cap = cv2.VideoCapture('pose/1.mp4')
# #     frames = []

# #     while cap.isOpened():
# #         success, frame = cap.read()
# #         if not success:
# #             break
# #         frame_resized = cv2.resize(frame, (540, 480))
# #         frames.append(frame_resized)

# #     cap.release()

# #     # Run analysis
# #     results = analyzer.analyze_video(frames, pose_estimator)

# #     # Show results summary
# #     import json
# #     print(json.dumps(results["summary"], indent=2))

# #     # Optional: display annotated video (optional for debug)
# #     # for idx, frame in enumerate(frames):
# #     #     landmarks = pose_estimator.extract_keypoints(frame)
# #     #     frame_with_pose = pose_estimator.draw_pose(frame, landmarks)
# #     #     cv2.imshow("Pose", frame_with_pose)
# #     #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #     #         break
# #     # cv2.destroyAllWindows()
from typing import Dict, Tuple, List
from analysis.squat_analyzer import SquatAnalyzer
from analysis.pushup_analyzer import PushupAnalyzer

class ExerciseAnalyzer:
    def __init__(self):
        self.squat = SquatAnalyzer()
        self.pushup = PushupAnalyzer()
        self.results = {
            "summary": {
                "squats": {"total_reps": 0, "good_form_reps": 0, "common_issues": []},
                "pushups": {"total_reps": 0, "good_form_reps": 0, "common_issues": []}
            },
            "frame_data": []
        }

    def analyze_video(self, frames: List, pose_estimator) -> Dict:
        for idx, frame in enumerate(frames):
            landmarks = pose_estimator.extract_keypoints(frame)
            if landmarks:
                self._process("squat", idx, landmarks, self.squat.analyze)
                self._process("pushup", idx, landmarks, self.pushup.analyze)
        return self.results

    def _process(self, exercise: str, idx: int, lm: Dict, analyzer_fn):
        did_rep, angle, issues, count_it = analyzer_fn(lm)
        if count_it:
            self.results["summary"][f"{exercise}s"]["total_reps"] += 1
            if not issues:
                self.results["summary"][f"{exercise}s"]["good_form_reps"] += 1
            else:
                self.results["summary"][f"{exercise}s"]["common_issues"].extend(issues)

            self.results["frame_data"].append({
                "frame_index": idx,
                "exercise": exercise,
                "rep_id": self.squat.rep_count if exercise == "squat" else self.pushup.rep_count,
                "is_form_ok": not issues,
                "angles": {"knee" if exercise == "squat" else "elbow": angle},
                "issues": issues
            })
