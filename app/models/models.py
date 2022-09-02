from pydantic import BaseModel

# Reference to MENSAJES_SIN_FILTRAR
class Mensajes(BaseModel):
    id: int
    contenido: str
    estado: int
    fecha_inclusion: str
    usuario: str

# Reference to FILTER_USERS
class Users(BaseModel):
    id: int
    username: str
    password: str
    state: int
    email: str
    description: str
    role: str
    
# Reference to DICCIONARIO_TELETON
class Diccionario(BaseModel):
    palabra:str
    usuario:str

