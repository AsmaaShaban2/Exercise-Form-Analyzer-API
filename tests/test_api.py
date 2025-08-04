import os
import io
import pytest
from api.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_analyze_endpoint_success(client):
    test_video_path = "demo/1.mp4"
    assert os.path.exists(test_video_path), "Missing test video."

    with open(test_video_path, 'rb') as video_file:
        data = {
            'video': (io.BytesIO(video_file.read()), '1.mp4')
        }
        response = client.post('/analyze', content_type='multipart/form-data', data=data)

    assert response.status_code == 200
    json_data = response.get_json()
    assert "video_id" in json_data
    assert "summary" in json_data
    assert "frame_data" in json_data
    assert isinstance(json_data["summary"], dict)
    assert isinstance(json_data["frame_data"], list)

def test_analyze_endpoint_no_file(client):
    response = client.post('/analyze')
    assert response.status_code == 400
    assert "error" in response.get_json()
