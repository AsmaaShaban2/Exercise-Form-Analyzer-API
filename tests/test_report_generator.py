import os
import shutil
import json
import pytest
import numpy as np
import cv2
from report.report_generator import save_json_and_csv, generate_pdf_report

TEST_OUTPUT_DIR = "test_reports"

# Sample mock result for testing
mock_results = {
    "summary": {
        "squats": {
            "total_reps": 2,
            "good_form_reps": 1,
            "common_issues": ["KNEE_OVER_TOE"]
        },
        "pushups": {
            "total_reps": 1,
            "good_form_reps": 1,
            "common_issues": []
        }
    },
    "frame_data": [
        {
            "frame_index": 0,
            "exercise": "squat",
            "rep_id": 1,
            "is_form_ok": False,
            "angles": {"knee": 95},
            "issues": ["KNEE_OVER_TOE"]
        },
        {
            "frame_index": 1,
            "exercise": "pushup",
            "rep_id": 1,
            "is_form_ok": True,
            "angles": {"elbow": 170},
            "issues": []
        }
    ]
}

@pytest.fixture
def clean_test_dir():
    # Ensure test directory is clean
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    yield
    shutil.rmtree(TEST_OUTPUT_DIR)

def test_save_json_and_csv(clean_test_dir):
    video_id = "test123"
    summary_path, csv_path = save_json_and_csv(mock_results, video_id, TEST_OUTPUT_DIR)

    assert os.path.exists(summary_path)
    assert os.path.exists(csv_path)

    # Check JSON content
    with open(summary_path, 'r') as f:
        summary = json.load(f)
        assert summary["squats"]["total_reps"] == 2

def test_generate_pdf_report(clean_test_dir):
    video_id = "test123"

    # Create dummy frames
    dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    frames = [dummy_frame.copy() for _ in range(2)]

    pdf_path = generate_pdf_report(video_id, mock_results, frames, TEST_OUTPUT_DIR)

    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")
    assert os.path.getsize(pdf_path) > 1000  # Not empty
