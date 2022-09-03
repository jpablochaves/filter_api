"""
    utils.py
    Manejo de ciertos utilitarios como:
    - Cargado de configuración    
"""
import configparser
import os
import logging
import hashlib
from logging.handlers import RotatingFileHandler

#SETTINGS_FILENAME = 'settings.ini'
# De esta manera se ubica sobre el root del proyecto y no sobre /app
SETTINGS_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', '.settings.ini'))
LOGS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'logs'))


def isSettingsFileThere(filename=SETTINGS_FILENAME) -> bool:
    """
    Revisar si existe o no el archivo de settings
    Args:
        filename (str,optional): El archivo o ruta del settings. Defaults to SETTINGS_FILENAME.    

    Raises:
        AssertionError: Si falla el assert de os.path.exists del path del archivo de settings

    Returns:
        bool: True si se encuentra el archivo, False si no se encuentra el archivo settings
    """   
    try:
        assert os.path.exists(filename)
        return True
    except AssertionError:
        logging.error(f'The settings file located at {filename} does not exist!')
        return False


def isLogsDirectoryThere(filename=LOGS_DIRECTORY) -> bool:
    """
    Revisar si existe o no el archivo de settings
    Args:
        filename (str,optional): El archivo o ruta del settings. Defaults to SETTINGS_FILENAME.    

    Raises:
        AssertionError: Si falla el assert de os.path.exists del path del archivo de settings

    Returns:
        bool: True si se encuentra el archivo, False si no se encuentra el archivo settings
    """
    try:
        assert os.path.exists(filename)
        return True
    except AssertionError:
        logging.error(f'The logs directory should exist at the following location: {filename}')
        return False


def load_db_config() -> dict:
    """
    Cargar la configuración de la BD del proyecto

    Returns:
        dict: diccionario con la configuración de la BD
    """
    configuration = {}
    config = configparser.ConfigParser()
    if not isSettingsFileThere(SETTINGS_FILENAME):
        print('*** ERROR ***, settings file not located!')
        return {}
    config.read(SETTINGS_FILENAME)
    ambient = config.getboolean('GLOBAL', 'PRODUCTION')
    if ambient == True:
        configuration = {
            "HOSTNAME": config.get('DATABASE-PROD', 'DB_HOST'),
            "PORT": config.get('DATABASE-PROD', 'DB_PORT'),
            "SID": config.get('DATABASE-PROD', 'DB_SID'),
            "USERNAME": config.get('DATABASE-PROD', 'DB_USER'),
            "PASSWORD": config.get('DATABASE-PROD', 'DB_PASSWORD'),
            "DEBUG": config.getboolean('GLOBAL', 'DEBUG'),
            "LOG_ROTATE": config.getboolean('GLOBAL', 'LOG_ROTATE')
        }
    else:
        configuration = {
            "HOSTNAME": config.get('DATABASE-TEST', 'DB_HOST'),
            "PORT": config.get('DATABASE-TEST', 'DB_PORT'),
            "SID": config.get('DATABASE-TEST', 'DB_SID'),
            "USERNAME": config.get('DATABASE-TEST', 'DB_USER'),
            "PASSWORD": config.get('DATABASE-TEST', 'DB_PASSWORD'),
            "DEBUG": config.getboolean('GLOBAL', 'DEBUG'),
            "LOG_ROTATE": config.getboolean('GLOBAL', 'LOG_ROTATE')
        }
    return configuration


def get_logger_dictConfig(useLogRotate:bool=False) -> dict:
    dictConfig = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s|%(levelname)s|%(module)s - %(lineno)d: %(message)s",
                "datefmt": "'%Y-%m-%d %H:%M:%S'"
            }
        },
        "handlers": {
            "console": {
                "level": logging.DEBUG,
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "logRotation": {
                "level": logging.DEBUG,
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "default",
                "filename": os.path.join(LOGS_DIRECTORY, "teleton_smsapi.log"),
                "when": "midnight",
                "interval": 1,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "uvicorn.full_logger": {
                "handlers": ["logRotation"] if useLogRotate else ["console"],
                "level": logging.DEBUG,
                "propagate": False
            },
            "uvicorn.discrete_logger": {
                "handlers": ["logRotation"] if useLogRotate else ["console"],
                "level": logging.ERROR,
                "propagate": False
            }
        },
        "root": {
            "level": logging.DEBUG,
            "handlers": ["logRotation"] if useLogRotate else ["console"]
        }
    }
    return dictConfig

def getLoggerLevel(currentConf:dict):
    """
    Retorna el logger que se debe usar
    Args:
        currentConf (dict): Recibe el dict con la configuracion actual

    Returns:
        str: segun el DEBUG de settings retorna o discrete_logger o full_loger
    """
    if currentConf['DEBUG'] == True:
        return 'uvicorn.full_logger'
    else:
        return 'uvicorn.discrete_logger'
    

def get_sha256str(input:str) -> str:
    """
    Obtener el hex digest sha256 a partir de un texto plano
    Args:
        input (str): Texto a convertir en str
    Returns:
        str: Texto en sha256
    """
    return hashlib.sha256(input.encode('utf-8')).hexdigest()


