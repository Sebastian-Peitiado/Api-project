from bson import ObjectId
from pymongo import MongoClient
from infrastructure.database_conextion import get_usuarios_collection
from src.main import app
from fastapi.testclient import TestClient
import os

os.environ["DB_NAME"] = os.getenv("DB_TEST_NAME", "test_db")

def crear_usuario():
    col = get_usuarios_collection()
    return str(col.insert_one({"name": "Juan", "lastName": "Pérez"}).inserted_id)


client = TestClient(app)


def test_nombre_incompleto():
    data = {"name":"","lastName":"Peitiado"}
    response = client.post("/Usuarios", json=data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("El nombre no puede estar vacío" in error.get("msg", "") for error in errors)

def test_apellido_incompleto():
    data = {"name":"Sebas","lastName":""}
    response = client.post("/Usuarios", json=data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    
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

def test_actualizacion_exitosa():
    user = crear_usuario()
    response = client.put(f"/modificar_usuarios/{user}", json={"name":"jorge","lastName":"peitiado"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "jorge"
    assert data["lastName"] == "peitiado"

def test_id_con_formato_incorrecto():
    response = client.put(f"/modificar_usuarios/3425", json={"name":"jorge","lastName":"peitiado"})
    assert response.status_code == 400
    assert response.json()["detail"] == "ID invalido"

def test_sin_aportar_datos():
    user = crear_usuario()
    response = client.put(f"/modificar_usuarios/{user}", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No se proporcionaron datos válidos para actualizar"

def test_id_inexistente():
    id_inexistente = str(ObjectId())
    response = client.put(f"/modificar_usuarios/{id_inexistente}", json={"name":"jorge","lastName":"peitiado"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"

def test_eliminacion_usuario():
    user = crear_usuario()
    response = client.delete(f"/eliminacion_usuario/{user}")
    assert response.status_code == 200
    collection = get_usuarios_collection()
    usuario = collection.find_one({"_id":ObjectId(user)})
    assert usuario is None

def test_eliminacion_usuario_id_erroneo():
    user = str(ObjectId)
    response = client.delete(f"/eliminacion_usuario/{user}")
    assert response.status_code == 404
    assert response.json()["detail"] == "ID invalido"
