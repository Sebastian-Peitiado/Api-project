from src.main import app
from fastapi.testclient import TestClient


client = TestClient(app)

def test_check_conection():
    response =  client.get("/health")
    assert response.json() == {"message": "Conexcion Establecida"}
    assert response.status_code == 200 


    
