from typing import Dict, List, Tuple
from analysis.angles import calculate_angle

class SquatAnalyzer:
    def __init__(self):
        self.state = "up"
        self.rep_count = 0

    def analyze(self, lm: Dict) -> Tuple[bool, float, List[str], bool]:
        try:
            hip = [lm["LEFT_HIP"]['x'], lm["LEFT_HIP"]['y']]
            knee = [lm["LEFT_KNEE"]['x'], lm["LEFT_KNEE"]['y']]
            ankle = [lm["LEFT_ANKLE"]['x'], lm["LEFT_ANKLE"]['y']]

            angle = calculate_angle(hip, knee, ankle)
            transition = False

            if self.state == "up" and angle < 100:
                self.state = "down"
            elif self.state == "down" and angle > 160:
                self.state = "up"
                self.rep_count += 1
                transition = True

            if transition:
                issues = []
                if angle > 100:
                    issues.append("INSUFFICIENT_DEPTH")
                if abs(knee[0] - ankle[0]) > 0.2:
                    issues.append("KNEE_OVER_TOE")
                return True, angle, issues, True

            return False, angle, [], False
        except KeyError:
            return False, 0, [], False
