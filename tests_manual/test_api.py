from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from infrastructure.database import Base
from presentation.dependencies import get_db


def create_owner(client):
    response = client.post("/api/v1/owners", json={"rut": "15111222-3", "nombre_completo": "Carlos Pinto", "telefono": "+56912345678", "direccion": "Av. Alemania 123"})
    assert response.status_code == 201
    return response.json()


def create_student(client):
    response = client.post("/api/v1/students", json={"rut": "19123456-7", "nombre_completo": "Valentina Rojas", "correo": "vrojas@example.cl", "anio_ingreso": 2024})
    assert response.status_code == 201
    return response.json()


def create_pet(client, owner_id, name="Rex", species="Perro", weight=12.5):
    return client.post("/api/v1/pets", json={"nombre": name, "especie": species, "raza": "Mestizo", "peso_kg": weight, "dueno_id": owner_id})


def test_crud_completo_de_mascota(client):
    owner = create_owner(client)
    created = create_pet(client, owner["id"])
    assert created.status_code == 201
    pet = created.json()
    assert pet["nombre"] == "Rex" and pet["dueno_id"] == owner["id"]
    assert client.get(f"/api/v1/pets/{pet['id']}").status_code == 200
    updated = client.put(f"/api/v1/pets/{pet['id']}", json={"nombre": "Rex II", "especie": "Perro", "raza": "Mestizo", "peso_kg": 14, "dueno_id": owner["id"]})
    assert updated.status_code == 200 and updated.json()["nombre"] == "Rex II"
    assert client.delete(f"/api/v1/pets/{pet['id']}").status_code == 204
    assert client.get(f"/api/v1/pets/{pet['id']}").status_code == 404


def test_validacion_de_datos_de_entrada(client):
    invalid = client.post("/api/v1/owners", json={"rut": "x", "nombre_completo": "A", "telefono": "1", "direccion": "x"})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
    invalid_email = client.post("/api/v1/students", json={"rut": "19123456-7", "nombre_completo": "Valentina Rojas", "correo": "no-es-correo", "anio_ingreso": 2024})
    assert invalid_email.status_code == 422


def test_relaciones_requieren_registros_existentes(client):
    assert create_pet(client, 999).status_code == 404
    owner = create_owner(client)
    pet = create_pet(client, owner["id"]).json()
    consultation = client.post("/api/v1/consultations", json={"fecha_hora": (datetime.now() + timedelta(days=1)).isoformat(), "motivo": "Control preventivo", "mascota_id": pet["id"], "estudiante_id": 999})
    assert consultation.status_code == 404


def test_reglas_de_fecha_y_transicion_de_estado(client):
    owner, student = create_owner(client), create_student(client)
    pet = create_pet(client, owner["id"]).json()
    base = {"motivo": "Control preventivo", "mascota_id": pet["id"], "estudiante_id": student["id"]}
    past = client.post("/api/v1/consultations", json={**base, "fecha_hora": (datetime.now() - timedelta(days=1)).isoformat()})
    assert past.status_code == 400
    created = client.post("/api/v1/consultations", json={**base, "fecha_hora": (datetime.now() + timedelta(days=1)).isoformat()})
    assert created.status_code == 201
    consultation_id = created.json()["id"]
    assert client.patch(f"/api/v1/consultations/{consultation_id}", json={"estado": "realizada"}).status_code == 200
    assert client.patch(f"/api/v1/consultations/{consultation_id}", json={"estado": "pendiente"}).status_code == 400


def test_filtro_ordenamiento_y_paginacion_de_mascotas(client):
    owner = create_owner(client)
    assert create_pet(client, owner["id"], "Rex", "Perro", 12).status_code == 201
    assert create_pet(client, owner["id"], "Luna", "Gato", 4).status_code == 201
    assert create_pet(client, owner["id"], "Thor", "Perro", 18).status_code == 201
    response = client.get("/api/v1/pets?especie=Perro&sort_by=peso_kg&order=desc&limit=1&skip=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2 and len(data["items"]) == 1
    assert data["items"][0]["nombre"] == "Thor"
    assert data["skip"] == 0 and data["limit"] == 1


def test_crud_de_estudiante_dueno_y_consulta(client):
    student, owner = create_student(client), create_owner(client)
    pet = create_pet(client, owner["id"]).json()
    assert client.get(f"/api/v1/students/{student['id']}").status_code == 200
    update = client.put(f"/api/v1/students/{student['id']}", json={"rut": student["rut"], "nombre_completo": "Valentina Rojas", "correo": "valentina@example.cl", "anio_ingreso": 2024})
    assert update.status_code == 200
    assert client.get(f"/api/v1/owners/{owner['id']}").status_code == 200
    owner_update = client.put(f"/api/v1/owners/{owner['id']}", json={"rut": owner["rut"], "nombre_completo": "Carlos Pinto", "telefono": "+56912345679", "direccion": "Av. Alemania 123"})
    assert owner_update.status_code == 200
    consultation = client.post("/api/v1/consultations", json={"fecha_hora": (datetime.now() + timedelta(days=3)).isoformat(), "motivo": "Revisión general", "mascota_id": pet["id"], "estudiante_id": student["id"]})
    assert consultation.status_code == 201
    consultation_id = consultation.json()["id"]
    assert client.get(f"/api/v1/consultations/{consultation_id}").status_code == 200
    assert client.patch(f"/api/v1/consultations/{consultation_id}", json={"diagnostico": "Sin hallazgos"}).status_code == 200
    assert client.delete(f"/api/v1/consultations/{consultation_id}").status_code == 204
    assert client.delete(f"/api/v1/pets/{pet['id']}").status_code == 204
    assert client.delete(f"/api/v1/owners/{owner['id']}").status_code == 204
    assert client.delete(f"/api/v1/students/{student['id']}").status_code == 204


def test_registros_persisten_al_reiniciar_cliente(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'persistencia.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as first_client:
            owner = create_owner(first_client)
            pet = create_pet(first_client, owner["id"]).json()
        # Un segundo cliente representa el reinicio del servidor: abre nuevas sesiones y consulta la misma BD.
        with TestClient(app) as restarted_client:
            response = restarted_client.get(f"/api/v1/pets/{pet['id']}")
            assert response.status_code == 200
            assert response.json()["nombre"] == "Rex"
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
