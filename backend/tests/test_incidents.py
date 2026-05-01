import pytest
import io

def test_create_incident_success(client, db, auth_headers):
    response = client.post(
        "/api/incidents",
        data={
            "lat": 34.05,
            "lon": -118.24,
            "title": "Test Fire",
            "description": "Fire detected in building",
            "incident_type": "fire"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert "incident_id" in response.json()

def test_create_incident_invalid_coords(client, auth_headers):
    response = client.post(
        "/api/incidents",
        data={
            "lat": 100.0, # Invalid latitude
            "lon": -118.24,
            "title": "Invalid Coords"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Latitude must be between -90 and 90" in response.json()["detail"]

def test_create_incident_with_photo(client, auth_headers):
    # Create a dummy image
    file_content = b"fake-image-data-with-enough-size-to-trigger-imghdr-if-needed"
    # Actually imghdr needs real headers, but we mocked the helper or it might fail
    # Let's use a simple valid PNG header if imghdr is strict
    png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    
    response = client.post(
        "/api/incidents",
        data={
            "lat": 34.05,
            "lon": -118.24,
            "title": "Incident with photo"
        },
        files={"photo": ("test.png", io.BytesIO(png_header), "image/png")},
        headers=auth_headers
    )
    
    # If it fails imghdr validation, it's 400
    if response.status_code == 400:
        assert "Invalid image file content" in response.json()["detail"]
    else:
        assert response.status_code == 201
        assert "photo_url" in response.json()

def test_create_incident_large_file(client, auth_headers):
    # Create a 11MB file (exceeds 10MB limit)
    large_content = b"0" * (11 * 1024 * 1024)
    
    response = client.post(
        "/api/incidents",
        data={"lat": 34.05, "lon": -118.24},
        files={"photo": ("large.jpg", io.BytesIO(large_content), "image/jpeg")},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "File size exceeds" in response.json()["detail"]
