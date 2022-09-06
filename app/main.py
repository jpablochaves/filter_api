import sys
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.config import dictConfig
import uvicorn
from app.routes.filtrado import filtradoApp
from app.routes.filtradoInterno import filtradoInternoApp
from app.database.database import start_dbpool, close_dbpool
from app.shared.utils import load_db_config, isSettingsFileThere, isLogsDirectoryThere, get_logger_dictConfig, getLoggerLevel

__REST_URI = '/v1/teleton/filtrado'
__REST_URI_INTERNAL = f'{__REST_URI}/interno'

app = FastAPI(title="FilterAPI", version=1.0)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Locate first the settings file
if isSettingsFileThere() == False:
    sys.exit("No settings file located")
elif isLogsDirectoryThere() == False:
    sys.exit("No logs directory located")
# Configure logging using a dictionary.
conf = load_db_config()
if conf['LOG_ROTATE'] == True:
    dictConfig(get_logger_dictConfig(True))
else:
    dictConfig(get_logger_dictConfig(False))
# Set the logger to use as part of the dictConfig
logger = logging.getLogger(getLoggerLevel(conf))


@app.on_event("startup")
def startup():
    start_dbpool()
    logger.info("Initializing API worker (DB Pool init)")


@app.on_event("shutdown")
def shutdown():
    close_dbpool()
    logger.info("Stopping API Worker (DB Pool closed)")


@app.get("/")
def test_endpoint(request: Request):
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": f"OK from {request.client.host}"})


# incluir mis operaciones del URI /v1/teleton/filtrado que se encuentran en filtrado.py
app.include_router(filtradoApp, prefix=__REST_URI)
app.include_router(filtradoInternoApp, prefix=__REST_URI_INTERNAL)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
