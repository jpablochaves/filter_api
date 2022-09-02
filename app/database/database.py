import cx_Oracle
from ..shared.utils import load_db_config
import logging as logger


db_pool = None

def init_session(connection, requestedTag_ignored):
    cursor = connection.cursor()
    cursor.execute("""ALTER SESSION SET NLS_DATE_FORMAT = 'DD/MM/YYYY HH24:MI'""")

def start_dbpool():
    conf = load_db_config()
    pool_min = 4
    pool_max = 4
    pool_inc = 1
    pool_gmd = cx_Oracle.SPOOL_ATTRVAL_WAIT

    username = conf['USERNAME']
    password = conf['PASSWORD']
    host = conf['HOSTNAME']
    port = conf['PORT']
    sid = conf['SID']
    # dsn -> connect string
    connect_string = cx_Oracle.makedsn(host, port, sid=sid)

    global db_pool
    try:
        db_pool = cx_Oracle.SessionPool(user=username,
                                        password=password,
                                        dsn=connect_string,
                                        min=pool_min,
                                        max=pool_max,
                                        increment=pool_inc,
                                        getmode=pool_gmd,
                                        homogeneous=False,
                                        session_callback=init_session,
                                        encoding="UTF-8")
        #logger.info(f"DB|OK|Connected to: {connect_string}")
        logger.info(f"DB|OK|Succesful Database Connection!")
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR: DB Pool failed to initialize {connect_string}, error_message: {dberr}")
        db_pool = None

def close_dbpool():
    try:
        if db_pool is None:
            logger.warning("Warning|DB|Pool is not alive! ")
        else:
            db_pool.close()
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR: DB Pool failed to stop, error_message: {dberr}")

"""
------------------------------------
    OPERACIONES HACIA LA BD
------------------------------------
"""
def authenticate_user(username:str) -> tuple:
    """
    Obtener un usuario y password en sha256 para que se compare con secrets.compare_digest
    Args:
            username (str): nombre de usuario que se desea obtener
    Returns:
            tuple: tupla con el formato: ('usuario','contraseña')
    """
    data = None
    if db_pool is None:
        logger.error("ERROR|DB|Pool is not established for authenticate_user")
        return data
    try:
        connection = db_pool.acquire()
        cursor = connection.cursor()
        usr = username.lower();
        sql = "SELECT USERNAME,PASSWORD FROM SMSATLANTIS.FILTER_USERS WHERE LOWER(USERNAME) = :usr AND STATE='A'"
        cursor.execute(sql, [usr])
        data = cursor.fetchone()
        db_pool.release(connection)
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR|authenticate_user()|Problem on SessionPool.acquire(), error_message: {dberr}")
        data = None
    return data

def fetch_message() -> dict:
    """
    Obtener un un SMS en estado 0 (sin filtrar) para mostrarlo en la aplicación de filtrado

    Returns:
            dict: Diccionario con formato JSON de: {"id":000,"contenido":"","fecha_inclusion":"DD/MM/YYYY HH24:MI:SS"}
    """
    data = None
    if db_pool is None:
        logger.error("ERROR|DB|Pool is not established for fetch_message")
        return data
    try:
        connection = db_pool.acquire()
        cursor = connection.cursor()
        sql = "SELECT id,contenido,TO_CHAR(FECHA_INCLUSION,'DD/MM/YYYY HH24:MI:SS') as fecha_inclusion FROM SMSATLANTIS.MENSAJES_SIN_FILTRAR WHERE ESTADO = 0 AND ROWNUM = 1"
        cursor.execute(sql)
        # Create dictionary from response
        cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
        data = cursor.fetchall()
        db_pool.release(connection)
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR|fetch_message()|Problem on SessionPool.acquire(), error_message: {dberr}")
        data = None
    finally:
        sql = None
        cursor = None
    return data

def fetch_new_messages(total_sms:int = 10) -> dict:
    """
    Obtener un listado de SMS en estado 0 (sin filtrar) para mostrarlos
    en la aplicación de filtrado
    Args:
            total_sms (int,optional): Default es 10. Define la cantidad de SMS que se quieren obtener en estado 0
    Returns:
            dict: Diccionario con formato JSON de: {"id":000,"contenido":"","fecha_inclusion":"DD/MM/YYYY HH24:MI:SS"}
    """
    data = None
    if db_pool is None:
        logger.error("ERROR|DB|Pool is not established for fetch_new_messages")
        return data
    try:
        connection = db_pool.acquire()
        cursor = connection.cursor()
        sql = "SELECT ID,CONTENIDO, TO_CHAR(FECHA_INCLUSION,'DD/MM/YYYY HH24:MI:SS') as FECHA_INCLUSION FROM SMSATLANTIS.MENSAJES_SIN_FILTRAR WHERE ESTADO = 0 AND ROWNUM <= :total_pag"
        total_pag = total_sms
        cursor.execute(sql, [total_pag])
        # Create dictionary from response
        cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
        data = cursor.fetchall()
        db_pool.release(connection)
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR|fetch_new_messages()|Problem on SessionPool.acquire(), error_message: {dberr}")
        data = None
    finally:
        sql = None
        cursor = None
        total_pag = None
    return data

#
# Utilizado para obtener los datos del mensaje que se va a actualizar
#
def get_message(id_sms:int) -> dict:
    """
    Obtener un un SMS en estado 0 (sin filtrar) para mostrarlo en la aplicación de filtrado
    Args:
        id_sms (int):  Id del SMS a buscar
    Returns:
            dict: Diccionario con formato JSON de: {"id":000,"contenido":"","fecha_inclusion":"DD/MM/YYYY HH24:MI:SS"}
    """
    data = None
    if db_pool is None:
        logger.error("ERROR|DB|Pool is not established for get_message")
        return data
    try:
        connection = db_pool.acquire()
        cursor = connection.cursor()
        sql = "SELECT ID,CONTENIDO, TO_CHAR(FECHA_INCLUSION,'DD/MM/YYYY HH24:MI:SS') as FECHA_INCLUSION FROM SMSATLANTIS.MENSAJES_SIN_FILTRAR WHERE ID = :id_sms"
        cursor.execute(sql, [id_sms])
        # Create dictionary from response
        cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
        data = cursor.fetchall()
        db_pool.release(connection)
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR|get_message()|Problem on SessionPool.acquire(), error_message: {dberr}")
        data = None
    finally:
        sql = None
        cursor = None
    return data


def fetch_user(username:str) -> dict:
    """
    Obtener un usuario segun su username
    Args:
            username (str): nombre de usuario que se desea obtener
    Returns:
            dict: Diccionario con formato JSON de: {"id":000,"contenido":"","fecha_inclusion":"DD/MM/YYYY HH24:MI:SS"}
    """
    data = None
    if db_pool is None:
        logger.error("ERROR|DB|Pool is not established for fetch_user")
        return data
    try:
        connection = db_pool.acquire()
        cursor = connection.cursor()
        usr = username.lower();
        sql = "SELECT ID,USERNAME,STATE,EMAIL,DESCRIPTION,ROLE FROM SMSATLANTIS.FILTER_USERS WHERE LOWER(USERNAME) = :usr"
        cursor.execute(sql, [usr])
        # Create dictionary from response
        cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
        data = cursor.fetchall()
        db_pool.release(connection)
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR|fetch_user()|Problem on SessionPool.acquire(), error_message: {dberr}")
        data = None
    finally:
        sql = None
        cursor = None
        usr = None
    return data

def approve_sms(id:int, user:str) -> bool:
    """
    Actualizar un mensaje a aprobado
    Args:
            id (int): id del sms que se desea aprobar
            user (str): usuario que actualiza el mensaje
    Returns:
            bool: True si se actualizo, False si falló
    """
    ret = False
    if db_pool is None:
        logger.error("ERROR|DB|Pool is not established for approve_sms")
        return ret
    try:
        connection = db_pool.acquire()
        cursor = connection.cursor()
        sql = "UPDATE SMSATLANTIS.MENSAJES_SIN_FILTRAR SET ESTADO = 2, USUARIO = :1 WHERE ID = :2"
        cursor.execute(sql, (user,id))
        connection.commit()
        rows = cursor.rowcount
        db_pool.release(connection)
        if rows > 0:
            ret = True
        else:
            ret = False
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR|approve_sms()|Problem on SessionPool.acquire(), error_message: {dberr}")
        ret = False
    return ret

def reject_sms(id:int, user:str) -> bool:
    """
    Actualizar un mensaje a rechazado
    Args:
            id (int): id del sms que se desea aprobar
            user (str): usuario que actualiza el mensaje
    Returns:
            bool: True si se actualizo, False si falló
    """
    ret = False
    if db_pool is None:
        logger.error("ERROR|DB|Pool is not established for reject_sms")
        return ret
    try:
        connection = db_pool.acquire()
        cursor = connection.cursor()
        sql = "UPDATE SMSATLANTIS.MENSAJES_SIN_FILTRAR SET ESTADO = 3, USUARIO = :1 WHERE ID = :2"
        cursor.execute(sql, (user,id))
        connection.commit()
        rows = cursor.rowcount
        db_pool.release(connection)
        if rows > 0:
            ret = True
        else:
            ret = False
    except (Exception, cx_Oracle.DatabaseError) as dberr:
        logger.error(f"DB|ERROR|reject_sms()|Problem on SessionPool.acquire(), error_message: {dberr}")
        ret = False
    return ret

def add_to_dictionary(word:str, user:str) -> int:
    """
    Actualizar un mensaje a rechazado
    Args:
            word (str): palabra que se va a agregar al diccionario
            user (str): usuario que actualiza el mensaje
    Returns:
            int: 0: Error: la palabra ya existe
                -1: Error Indefinido: Error no controlado
                1: OK: Se agregó la palabra
    """
    ret = -1
    if db_pool is None:
        logger.error("ERROR|DB|Pool is not established for add_to_dictionary")
        return ret
    try:
        connection = db_pool.acquire()
        cursor = connection.cursor()
        sql = "INSERT INTO SMSATLANTIS.DICCIONARIO_TELETON (PALABRA,USUARIO) VALUES (:palabra,:usuario)"
        cursor.execute(sql, (word,user))
        connection.commit()
        db_pool.release(connection)
        ret = 1
    except cx_Oracle.IntegrityError as pkerr:
        logger.error(f"DB|ERROR|add_to_dictionary()|The word {word} already exists!, error_message: {pkerr}")
        ret = 0
    except cx_Oracle.DatabaseError as dberr:
        logger.error(f"DB|ERROR|add_to_dictionary()|Problem on SessionPool.acquire(), error_message: {dberr}")
        err = dberr.args
        if "ORA-00001" in err[0].message:
            ret = 0
        else:
            ret = -1
    return ret

