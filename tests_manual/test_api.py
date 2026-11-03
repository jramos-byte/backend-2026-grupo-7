import pytest

def test_create_and_get_pet_success (client):
    payload = {"name": "Firulais", "age": 3, "species": "Perro"}
    response = client.post("/pets/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Firulais"
    pet_id = data["id"]
    
    response = client.get(f"/pets/{pet_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Firulais"
    
def test_create_pet_invalid_data(client):
    payload = {"species": "Gato", "age": "No_es_un_numero"}
    response = client.post("/pets/", json=payload)
    assert response.status_code == 422      

def test_get_nonexistent_pet(client):
    response = client.get("/pets/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Pet not found"}
    
@pytest.fixture
def seed_data(client):
    pets = [
        {"name": "Firulais", "age": 3, "species": "Perro"},
        {"name": "Michi", "age": 2, "species": "Gato"},
        {"name": "Chill", "age": 5, "species": "Perro"}
    ]
    for pet in pets:
        client.post("/pets/", json=pet)
    return pets

def test_filters_sorting_and_pagination(client, seed_data):

    response = client.get("/pets/?species=Perro")
    assert response.status_code == 200
    results = response.json()["items"]
    assert len(results) == 2
    assert all(pet["species"] == "Perro" for pet in results)
    
    response = client.get("/pets/?sort_by=age&order=asc")
    assert response.status_code == 200
    results = response.json()["items"]
    ages = [pet["age"] for pet in results]
    assert ages == sorted(ages)
    
    response = client.get("/pets/?limit=2&skip=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 3
    
def test_persistance_after_api_restart(db_session,):
    from fastapi.testclient import TestClient
    from app.main import app
    from infrastructure.database import get_db

    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client1:
        payload = {"name": "Persistente", "age": 10, "species": "Loro"}
        res_create = client1.post("/pets/", json=payload)
        assert res_create.status_code == 201
        created_pet_id = res_create.json()["id"]

    app.dependency_overrides.clear()

    def override_get_db_2():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db_2

    with TestClient(app) as client2:
        res_get = client2.get(f"/pets/{created_pet_id}")
        assert res_get.status_code == 200
        assert res_get.json()["name"] == "Persistente"
        
    
