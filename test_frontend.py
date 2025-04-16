import io
import pytest
from frontend import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_keys(client, monkeypatch):
    # Monkey-patch requests.get to return a mock response
    class MockResponse:
        def __init__(self, json_data):
            self._json = json_data
            self.status_code = 200
        def json(self):
            return self._json

    def mock_get(url):
        return MockResponse({"public_key": "dummy_public", "private_key": "dummy_private"})
    
    monkeypatch.setattr("requests.get", mock_get)
    response = client.get("/generate_keys")
    data = response.get_json()
    assert data["public_key"] == "dummy_public"
    assert data["private_key"] == "dummy_private"

def test_sign_route(client, monkeypatch):
    def mock_post(url, files, data):
        # Simulate successful signature response
        class MockResponse:
            status_code = 200
            def json(self):
                return {"signature": "dummy_signature"}
        return MockResponse()
    
    monkeypatch.setattr("requests.post", mock_post)
    data = {
        "message": "Test message",
    }
    fake_file = (io.BytesIO(b"dummy private key content"), "private_key.pem", "application/x-pem-file")
    data_form = {'message': 'Test message'}
    # Simulate file upload
    response = client.post("/sign", 
                           data=dict(private_key=fake_file, message="Test message"),
                           content_type="multipart/form-data")
    result = response.get_json()
    assert result["signature"] == "dummy_signature"

def test_verify_route(client, monkeypatch):
    def mock_post(url, json):
        class MockResponse:
            status_code = 200
            def json(self):
                return {"valid": True}
        return MockResponse()
    
    monkeypatch.setattr("requests.post", mock_post)
    payload = {
        "public_key": "dummy_public",
        "message": "Test message",
        "signature": "dummy_signature"
    }
    response = client.post("/verify", json=payload)
    result = response.get_json()
    assert result["valid"] is True
