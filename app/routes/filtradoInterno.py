from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import logging as logger
from typing import List
from app.models.models import Mensajes, Users, Diccionario
from app.controllers.filtradoInternoController import get_new_sms_list,  get_new_sms, get_sms, approve_sms, reject_sms, add_dictionary
from app.controllers.authController import authenticate_user

filtradoInternoApp = APIRouter()
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    # Autentica contra la BD usando secrets.compare.digest
    if not authenticate_user(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@filtradoInternoApp.get('/')
def test_endpoint(request: Request):
    logger.info(f"Test endpoint from {request.client.host}")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": f"OK from {request.client.host}"})


@filtradoInternoApp.get("/sms/")
def getSMS(username: str = Depends(get_current_username), response_model=List[Mensajes], status_code=status.HTTP_200_OK):
    data = get_new_sms()
    if data is None:
        logger.error("ERROR|filtrado|data is None for message with status 0")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"error": "There are no messages with status 0 (non filtered) to display!"})
    else:
        return data


@filtradoInternoApp.get("/sms/list/")
def get_all_unfiltered_sms(quantity: int = 10, username: str = Depends(get_current_username), response_model=List[Mensajes], status_code=status.HTTP_200_OK):
    # quantity puede enviarse como param: /v1/teleton/filtrado/sms/list/?quantity=5
    data = get_new_sms_list(quantity)
    if data is None:
        logger.error(
            "ERROR|filtrado|list|data is None for messages with status 0")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "There are no messages with status 0 (non filtered) to display!"})
    else:
        return data


@filtradoInternoApp.put("/sms/approve/{sms_id}")
async def approveSMS(sms_id: int, username: str = Depends(get_current_username), response_model=List[Mensajes]):
    db_sms = get_sms(sms_id)
    if not db_sms:
        err_msg = f"SMS with id {sms_id} not found!"
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": err_msg})
    else:
        ret_data = approve_sms(sms_id, username)
        return JSONResponse(content=ret_data, status_code=status.HTTP_200_OK)


@filtradoInternoApp.put("/sms/reject/{sms_id}")
async def rejectSMS(sms_id: int, username: str = Depends(get_current_username), response_model=List[Mensajes]):
    db_sms = get_sms(sms_id)
    if not db_sms:
        err_msg = f"SMS with id {sms_id} not found!"
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": err_msg})
    else:
        ret_data = reject_sms(sms_id, username)
        return JSONResponse(content=ret_data, status_code=status.HTTP_200_OK)


@filtradoInternoApp.post("/sms/dictionary/")
async def addDictionary(datos_request: Diccionario, username: str = Depends(get_current_username)):
    ret_status = add_dictionary(datos_request)
    if ret_status == -1:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Error trying to add word to dictionary"})
    elif ret_status == 0:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": f"word {datos_request.palabra} already exists in the teleton dictionary"})
    else:
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"ok": f"{datos_request.palabra} succesfully added to teleton dictionary"})
