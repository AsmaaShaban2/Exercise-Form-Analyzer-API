"""
Flask API for Exercise Analysis Service
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import cv2
import numpy as np
import logging
import traceback
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from analysis.analyzer import ExerciseAnalyzer
from pose.pose_estimator import PoseEstimator
from analysis.video_exercise_analyzer import load_video_frames
import json
from report.report_generator import save_json_and_csv, generate_pdf_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
REPORT_FOLDER = os.getenv('REPORTS_FOLDER', 'reports')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'exercise-analysis-api',
        'version': '1.0.0'
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Exercise Analysis API',
        'version': '1.0.0',
        'description': 'Computer vision API for exercise form analysis',
        'endpoints': {
            'POST /analyze': 'Analyze exercise video',
            'GET /report/<video_id>': 'Download PDF report',
            'GET /health': 'Health check',
            'GET /': 'API information'
        },
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size': f"{app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB"
    }), 200

@app.route('/analyze', methods=['POST'])
def analyze_video():
    """
    Analyze exercise video for form and repetition counting.

    Expected: multipart/form-data with 'video' file
    Returns: JSON with analysis results
    """
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        video = request.files['video']

        # Check if file is selected
        if video.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Check file extension
        if not allowed_file(video.filename):
            return jsonify({
                "error": f"File type not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400

        filename = secure_filename(video.filename)
        video_id = str(uuid.uuid4())
        video_path = os.path.join(UPLOAD_FOLDER, f"{video_id}_{filename}")
        video.save(video_path)

        logger.info(f"Processing video: {video_path}")

        # Load and process video
        frames = load_video_frames(video_path)

        if not frames:
            return jsonify({"error": "Failed to process video or no frames extracted"}), 400

        pose_estimator = PoseEstimator(alpha=0.5)
        analyzer = ExerciseAnalyzer()
        results = analyzer.analyze_video(frames, pose_estimator)

        # Save data and PDF
        summary_path, csv_path = save_json_and_csv(results, video_id, REPORT_FOLDER)
        generate_pdf_report(video_id, results, frames, REPORT_FOLDER)

        logger.info(f"Analysis complete for video {video_id}")

        # Clean up uploaded file (optional)
        try:
            os.remove(video_path)
        except Exception as e:
            logger.warning(f"Failed to remove uploaded file: {e}")

        return jsonify({
            "video_id": video_id,
            "summary": results["summary"],
            "frame_data": results["frame_data"],
            "pdf_url": f"/report/{video_id}"
        })

    except RequestEntityTooLarge:
        return jsonify({"error": "File too large. Maximum size is 50MB"}), 413

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error during video processing"}), 500

@app.route('/report/<video_id>', methods=['GET'])
def download_report(video_id):
    """Download PDF report for a specific video analysis."""
    try:
        filename = f"{video_id}.pdf"
        file_path = os.path.join(REPORT_FOLDER, filename)

        if not os.path.exists(file_path):
            return jsonify({"error": "Report not found"}), 404

        return send_from_directory(REPORT_FOLDER, filename, as_attachment=True)

    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return jsonify({"error": "Failed to download report"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return jsonify({"error": "File too large. Maximum size is 50MB"}), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)


