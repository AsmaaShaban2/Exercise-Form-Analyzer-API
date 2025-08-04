from typing import Dict, List, Tuple
import numpy as np
from analysis.angles import calculate_angle, angle_between_vectors

class PushupAnalyzer:
    def __init__(self):
        self.state = "up"
        self.rep_count = 0

    def analyze(self, lm: Dict) -> Tuple[bool, float, List[str], bool]:
        try:
            shoulder = [lm["LEFT_SHOULDER"]['x'], lm["LEFT_SHOULDER"]['y']]
            elbow = [lm["LEFT_ELBOW"]['x'], lm["LEFT_ELBOW"]['y']]
            wrist = [lm["LEFT_WRIST"]['x'], lm["LEFT_WRIST"]['y']]
            hip = [lm["LEFT_HIP"]['x'], lm["LEFT_HIP"]['y']]
            ankle = [lm["LEFT_ANKLE"]['x'], lm["LEFT_ANKLE"]['y']]

            angle = calculate_angle(shoulder, elbow, wrist)
            transition = False

            if self.state == "up" and angle < 90:
                self.state = "down"
            elif self.state == "down" and angle > 160:
                self.state = "up"
                self.rep_count += 1
                transition = True

            if transition:
                vec1 = np.array(hip) - np.array(shoulder)
                vec2 = np.array(ankle) - np.array(hip)
                body_line_angle = angle_between_vectors(vec1, vec2)

                issues = []
                if abs(body_line_angle - 180) > 15:
                    issues.append("BODY_LINE_BREAK")
                if angle < 60:
                    issues.append("ELBOW_FLARE")

                return True, angle, issues, True

            return False, angle, [], False
        except KeyError:
            return False, 0, [], False
