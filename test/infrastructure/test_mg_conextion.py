from typing import Collection
from fastapi import Depends
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pytest

from infrastructure.database_conextion import get_mongo_client, insert_user_in_collection
from main import Usuario


def test_mongo_connection():
    client = get_mongo_client()
    try:
        # Esto lanza excepción si no hay conexión
        server_info = client.server_info()
        assert "version" in server_info
        print("✅ Conexión exitosa a MongoDB")
    except ConnectionFailure as e:
        pytest.fail(f"❌ Fallo al conectar a MongoDB: {e}")

def test_insertion_user_in_coleccion():
   user = Usuario(name="Sebas", lastName="Peitiado")
   response = insert_user_in_collection(user)
   assert response.inserted_id is not None


