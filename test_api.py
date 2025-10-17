# test_api.py
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_create_organizer():
    response = client.post("/organizers/", json={"name": "API Test Org", "contact_info": "api@test.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "API Test Org"
    assert "id" in data

def test_read_organizer():
    # Создаем организатора для тестирования
    response_create = client.post("/organizers/", json={"name": "Read Test Org", "contact_info": "read@test.com"})
    org_id = response_create.json()["id"]

    response = client.get(f"/organizers/{org_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org_id
    assert data["name"] == "Read Test Org"

def test_delete_organizer():
    # Создаем организатора для удаления
    response_create = client.post("/organizers/", json={"name": "Delete Test Org", "contact_info": None})
    org_id = response_create.json()["id"]

    response_delete = client.delete(f"/organizers/{org_id}")
    assert response_delete.status_code == 200
    assert response_delete.json() == {"detail": "Organizer deleted"}

    # Проверяем, что удален
    response_check = client.get(f"/organizers/{org_id}")
    assert response_check.status_code == 404
