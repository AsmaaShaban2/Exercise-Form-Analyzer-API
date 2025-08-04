from analysis.pushup_analyzer import PushupAnalyzer
from analysis.squat_analyzer import SquatAnalyzer

def test_pushup_fsm_transition():
    analyzer = PushupAnalyzer()
    landmarks = {
        "LEFT_SHOULDER": {'x': 0.5, 'y': 0.2},
        "LEFT_ELBOW": {'x': 0.5, 'y': 0.4},
        "LEFT_WRIST": {'x': 0.5, 'y': 0.6},
        "LEFT_HIP": {'x': 0.5, 'y': 0.8},
        "LEFT_ANKLE": {'x': 0.5, 'y': 1.0},
    }

    _, angle, issues, count_it = analyzer.analyze(landmarks)
    assert isinstance(angle, float)
    assert isinstance(issues, list)
    assert not count_it  # Still in initial state

def test_squat_fsm_transition():
    analyzer = SquatAnalyzer()
    landmarks = {
        "LEFT_HIP": {'x': 0.5, 'y': 0.3},
        "LEFT_KNEE": {'x': 0.5, 'y': 0.6},
        "LEFT_ANKLE": {'x': 0.5, 'y': 0.9},
    }

    _, angle, issues, count_it = analyzer.analyze(landmarks)
    assert isinstance(angle, float)
    assert isinstance(issues, list)
