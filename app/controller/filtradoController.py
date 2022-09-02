import app.database.database as db
from app.shared.utils import get_sha256str
from app.models.models import Diccionario
import logging as logger
import secrets

def get_new_sms_list(cantidad_lista:int = 10):
    """
        Retorna una lista JSON con el siguiente formato:
        {
        "ID": 12354,
        "CONTENIDO": "Yo dono 2000",
        "FECHA_INCLUSION": "2021-12-05T01:28:26"
        },
        {
        "ID": 123545,
        "CONTENIDO": "Yo dono 3000",
        "FECHA_INCLUSION": "2021-12-05T01:28:27"
        }
    Args:
        cantidad_lista (int,optional): default es 10. Especifica la cantidad de sms que desea obtener en el select
    Returns:
        dict: Diccionario con el formato especificado y la cantidad indicada

    """
    data = db.fetch_new_messages(cantidad_lista)
    return data

def get_new_sms():
    """
        Retorna un JSON con el siguiente formato:
        {
        "ID": 12354,
        "CONTENIDO": "Yo dono 2000",
        "FECHA_INCLUSION": "2021-12-05T01:28:26"
        }
    """
    data = db.fetch_message()
    return data

def get_sms(id:int) -> dict:
    """
        Retorna un JSON con el siguiente formato:
        {
        "ID": 12354,
        "CONTENIDO": "Yo dono 2000",
        "FECHA_INCLUSION": "2021-12-05T01:28:26"
        }
    Args:
        id (int):  el id del sms a buscar
    Returns:
        dict: Diccionario con el formato mencionado si se encuentra, None si no hay datos
    """
    data = db.get_message(id)
    if data is None or len(data) < 1:
        data = None
    return data

def authenticate_user(http_user:str,http_passwd:str) -> bool:
    """
       Ejecuta una autenticación contra la BD utilizando secrets.compare_digest para evitar timing attacks
       Compara contra lo que se obtiene de la BD -> tupla con (user,passwd)
       Returns:
           bool: True si el usuario autentica, False si no autentica
    """
    data = db.authenticate_user(http_user)
    if data is not None and len(data) != 0:
        return secrets.compare_digest(data[0], http_user) & secrets.compare_digest(data[1], get_sha256str(http_passwd))
    else:
        return False

def get_user(username:str):
    """
        Retorna un JSON con el siguiente formato:
        {
        "ID": "1",
        "USERNAME": "jdoe",
        "STATE": "A",
        "EMAIL": "johndoe@ice.go.cr",
        "DESCRIPTION": "Admin user for teleton",
        "ROLE": "FILTER"
    }
    """
    user_data = db.fetch_user(username)
    return user_data

def approve_sms(sms_id:int, username:str):
    """
        Retorna un JSON con el siguiente formato:
       {
        "ID": 12354,        ,
        "ESTADO": "APROBADO"
        }
    Args:
        sms_id (int): id del SMS que va a aprobar
        username (str): Nombre de usuario que actualiza
    """
    user_data = {}
    if db.approve_sms(sms_id,username):
        user_data = {"ID": sms_id, "ESTADO":"APROBADO"}
    else:
        user_data = {"ID": sms_id, "ESTADO":"FALLIDO"}
    return user_data

def reject_sms(sms_id:int, username:str):
    """
        Retorna un JSON con el siguiente formato:
       {
        "ID": 12354,        ,
        "ESTADO": "RECHAZADO"
        }
    Args:
        sms_id (int): id del SMS que va a aprobar
        username (str): Nombre de usuario que actualiza
    """
    user_data = {}
    if db.reject_sms(sms_id,username):
        user_data = {"id": sms_id, "estado":"rechazado"}
    else:
        user_data = {"id": sms_id, "estado":"error"}
    return user_data

def add_dictionary(datos_dict:Diccionario) -> int:
    """
        Obtiene un Objeto tipo Diccionario (palabra, usuario)
        y lo envia a la BD para ser agreagdo
        Args:
            datos_dict (Diccionario): Diccionario definido en models con palabra,usuario
        Returns:
            int: -1: Error indefinido - 0 Palabra ya registrada - 1 Palabra registrada
    """
    return db.add_to_dictionary(datos_dict.palabra,datos_dict.usuario)