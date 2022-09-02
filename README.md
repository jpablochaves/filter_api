# API Rest para Filtrado de Teletón | filter_api

## Filtra los mensajes que van a mostrar previamente en el cintillo de TV

**Dependencias** (_requirements.tx)

* Requerimientos 
> Se necesita tener instalado lo que se indica en el archivo requirements.txt

* Archivo de configuración
> Se necesita el archivo .settings.ini con la configuración de la Base de Datos a usar (no se incluye por seguridad). Este archivo debe de ir dentro de app/ y con el nombre .settings.ini

* *_Ejemplo de .settings.ini_*

[GLOBAL]\
PRODUCTION = true\
DEBUG = true\
LOG_ROTATE = true\
[DATABASE-TEST]\
DB_HOST=localhost\
DB_PORT=1521\
DB_SID=sid\
DB_USER=youruser\
DB_PASSWORD=yourpass\
[DATABASE-PROD]\
DB_HOST=localhost\
DB_PORT=1521\
DB_SID=sid\
DB_USER=youruser\
DB_PASSWORD=yourpass\

---


* Local test
> Si se va a ejecutar sin docker a modo de test es mejor de la siguiente manera: uvicorn app.main:app

**Docker**

* Construir la imagen
> docker build -t teleton-api . \
**Importante:** La imagen contiene la instalación del cliente de Oracle ya que este backend usa como DBMS Oracle, y es requerido para cx_Oracle

* Ejecutar la imagen docker del API en un puerto específico:
> docker run -d --name teleton-api -p 8000:8000 teleton-api

* Docker compose (si se desea desde el compose)
> Se encuentra el archivo docker-compose.yml en caso de querer utilizarlo para crear el API. Comando: docker compose up -d


#### Se realizó utilizando FastAPI con seguridad httpbasicauth
#### Más info
https://hub.docker.com/r/tiangolo/uvicorn-gunicorn-fastapi