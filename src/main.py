import re
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Path
from pymongo.collection import Collection
from pydantic import BaseModel, field_validator
from bson import ObjectId
from infrastructure.database_conextion import get_usuarios_collection, insert_user_in_collection

REGEX_SOLO_LETRAS = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$"
ALERT = "No se permiten caracteres especiales ni números en nombre o apellido"

class Usuario(BaseModel):
    name : str
    lastName : str

    @field_validator("name")
    def nombre_no_vacio(cls, v):
        if not v or v.strip() == "":
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()
    
    @field_validator("lastName")
    def apellido_no_vacio(cls, v):
        if not v or v.strip() == "":
            raise ValueError("El apellido no puede estar vacío")
        return v.strip()

    @field_validator("name", "lastName")
    def no_numeros(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError("No se aceptan numeros en los campos de nombre y apellido")
        return v

    @field_validator("name", "lastName")
    def no_caracteres(cls,v):
        if not re.match(REGEX_SOLO_LETRAS, v):
            raise ValueError(ALERT)
        return v

   


class UsuarioResponse(Usuario):
    id: str

class UsuarioUpdate(BaseModel):
    name: Optional[str] = None
    lastName: Optional[str] = None

    @field_validator("name", "lastName")
    def sin_campos_vacios(cls, v):
        if not v or v.strip() == "":
            raise ValueError("El apellido y el nombre no puede estar vacío")
        return v.strip()

    @field_validator("name", "lastName")
    def no_numeros(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError("No se aceptan numeros en los campos de nombre y apellido")
        return v

    @field_validator("name", "lastName")
    def no_caracteres(cls,v):
        if not re.match(REGEX_SOLO_LETRAS, v):
            raise ValueError(ALERT)
        return v
    

class EliminacionResponse(BaseModel):
    message: str


def modificar_usuario_en_db(usuario_id: str, datos: UsuarioUpdate, collection: Collection) -> UsuarioResponse:
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID invalido")

    usuario_existente = collection.find_one({"_id": ObjectId(usuario_id)})

    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nuevos_datos = {}
    if datos.name is not None:
        nuevos_datos["name"] = datos.name.strip()

    if datos.lastName is not None:
        nuevos_datos["lastName"] = datos.lastName.strip()

    if not nuevos_datos:
        raise HTTPException(status_code=400, detail="No se proporcionaron datos válidos para actualizar")

    result = collection.update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": nuevos_datos}
    )

    

    usuario_actualizado = collection.find_one({"_id": ObjectId(usuario_id)})

    return UsuarioResponse(
        id=str(usuario_actualizado["_id"]),
        name=usuario_actualizado["name"],
        lastName=usuario_actualizado["lastName"]
    )
   

def eliminacion_usuario(usuario_id : str, collection : Collection):
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=404, detail="ID invalido")

    resultado = collection.delete_one({"_id": ObjectId(usuario_id)})
    
    return {"message": "Usuario eliminado exitosamente"}


app = FastAPI()
@app.get("/health")
async def conexcion_check():
    return {"message":"Conexcion Establecida"}

@app.post("/Usuarios",  response_model=UsuarioResponse)
async def alta_usuario(user : Usuario):
    collection = get_usuarios_collection()
    result = insert_user_in_collection(user,collection)
    return UsuarioResponse(
        id=str(result.inserted_id),
        name=user.name,
        lastName=user.lastName
    )

@app.put("/modificar_usuarios/{usuario_id}",response_model=UsuarioResponse)
async def modificar_usuario(
    usuario_id: str = Path(..., description="ID del usuario a actualizar"),
    datos: UsuarioUpdate = ...,
    collection: Collection = Depends(get_usuarios_collection)
): 
    return modificar_usuario_en_db(usuario_id, datos, collection)

@app.delete("/eliminacion_usuario/{usuario_id}",response_model=EliminacionResponse)
async def elimininar_usuario(
    usuario_id: str = Path(..., description="ID del usuario a eliminar"),
    collection: Collection = Depends(get_usuarios_collection)
):
    return eliminacion_usuario(usuario_id, collection)