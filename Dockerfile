#FROM python:3.9-buster
FROM tiangolo/uvicorn-gunicorn:python3.9

# Installing Oracle instant client
WORKDIR    /opt/oracle
RUN ["chmod", "+x", "/opt/oracle"]
RUN        apt-get update && apt-get install -y libaio1 wget unzip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
            && unzip instantclient-basiclite-linuxx64.zip \
            && rm -f instantclient-basiclite-linuxx64.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig

# Install the fastapi application
WORKDIR /api

COPY ./requirements.txt /api/requirements.txt
COPY ./.settings.ini /api/.settings.ini
COPY ./app /api/app

# What you install on the terminal for the image. It tells pip to not use cache
RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt
RUN mkdir -p /api/logs \ 
    && > /api/logs/teleton_smsapi.log
RUN ["chmod", "+x", "/api"]
RUN ["chmod", "+x", "/api/logs"]

# Set the working path for PYTHONPATH that is used for fastapi
ENV PYTHONPATH "${PYTHONPATH}:/api/app"
# Set the timezone
# For alpine based images install first tzdata -> RUN apk add --no-cache tzdata
ENV TZ=America/Costa_Rica
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#Define the network ports that this container will listen on at runtime.
EXPOSE 8000
#CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Para ejecutarlo obteniendo el stdout stderr de los mensajes default de fastapi | sh -c Read commands from the command_string operand instead of from the standard # input.  Special parameter 0 will be set from the command_name operand and the positional parameters ($1, $2, etc.)  set from the remaining argument operands.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --reload >> /api/logs/teleton_smsapi.log 2>&1"]