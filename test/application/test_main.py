from bson import ObjectId
from pymongo import MongoClient
from infrastructure.database_conextion import get_usuarios_collection
from src.main import app
from fastapi.testclient import TestClient
import os

os.environ["DB_NAME"] = os.getenv("DB_TEST_NAME", "test_db")


def crear_usuario_prueba():
    collection = get_usuarios_collection()
    result = collection.insert_one({"name": "Juan", "lastName": "Pérez"})
    return str(result.inserted_id)


def eliminar_usuario_prueba(usuario_id):
    collection = get_usuarios_collection()
    collection.delete_one({"_id": ObjectId(usuario_id)})


client = TestClient(app)


def test_nombre_incompleto():
    data = {"name":"","lastName":"Peitiado"}
    response = client.post("/Usuarios", json=data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    # Busca que haya un error con ese mensaje
    assert any("El nombre no puede estar vacío" in error.get("msg", "") for error in errors)

def test_apellido_incompleto():
    data = {"name":"Sebas","lastName":""}
    response = client.post("/Usuarios", json=data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    # Busca que haya un error con ese mensaje
    assert any("El apellido no puede estar vacío" in error.get("msg", "") for error in errors)


def test_creacion_usuario_exitosa():
    datos_usuario = {"name": "Juan", "lastName": "Pérez"}
    response = client.post("/Usuarios", json=datos_usuario)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Juan"
    assert data["lastName"] == "Pérez"

def test_campos_faltantes():
    response = client.post("/Usuarios", json={})
    assert response.status_code == 422

# def test_actualizacion_exitosa():
#     usuario_id = crear_usuario_prueba()
#     response = client.put(f"/Usuarios/{usuario_id}", json={
#         "name": "Carlos",
#         "lastName": "Gómez"
#     })
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == usuario_id
#     assert data["name"] == "Carlos"
#     assert data["lastName"] == "Gómez"
#     eliminar_usuario_prueba(usuario_id)

