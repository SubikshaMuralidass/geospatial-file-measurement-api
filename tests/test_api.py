from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_invalid_file_id():
    response = client.get("/api/files/random-id")

    assert response.status_code == 200
    assert response.json() == {
        "message": "File not found."
    }


def test_invalid_measurement_file_id():
    response = client.get(
        "/api/files/random-id/measurements"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "File not found."
    }