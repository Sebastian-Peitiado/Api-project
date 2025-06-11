from pydantic import ValidationError
import main
from main import Usuario
import pytest


def test_user_name_cant_be_numbers():
    with pytest.raises(ValidationError):
        Usuario(name=2341,lastName="peitiado")
        

def test_user_lastName_cant_be_numbers():
    with pytest.raises(ValidationError):
        Usuario(name="sebas",lastName=3424)

def test_user_name_cant_include_numbers():
    with pytest.raises(ValidationError, match="No se aceptan numeros en los campos de nombre y apellido"):
        Usuario(name="1234", lastName="Peitiado")

def test_user_lastName_cant_include_numbers():
    with pytest.raises(ValidationError, match="No se aceptan numeros en los campos de nombre y apellido"):
        Usuario(name="Sebas", lastName="7645")