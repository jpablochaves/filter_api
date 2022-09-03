import app.database.database as db
from app.shared.utils import get_sha256str
import secrets


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