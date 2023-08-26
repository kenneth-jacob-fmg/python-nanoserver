FROM fmgaksacr.azurecr.io/python-nanoserver:3.9.13_1809

ENV SSL_CERTFILE "localhost+2.pem"
ENV SSL_KEYFILE "localhost+2-key.pem"

EXPOSE 80

WORKDIR C:\\website
COPY ./requirements.txt C:\\website\\requirements.txt
COPY ./logging.yaml C:\\website\\logging.yaml

RUN pip install uvicorn
RUN pip install --no-cache-dir --upgrade -r C:\\website\\requirements.txt

COPY ./app C:\\website\\app

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8432", "--workers", "4", "--log-config", "logging.yaml", "--ssl-certfile", "C:/container_ssl/$SSL_CERTFILE", "--ssl-keyfile", "C:/container_ssl/$SSL_KEYFILE"]

CMD uvicorn app.main:app --host 0.0.0.0 --port 8432 --workers 4 --log-config "C:/website/logging.yaml" --ssl-certfile "C:/container_byda/ssl/${SSL_CERTFILE}" --ssl-keyfile "C:/container_byda/ssl/${SSL_KEYFILE}"

# -----------------------------------------
# GCP deployment build without SSL certificate
# -----------------------------------------
#CMD uvicorn app.main:app --host 0.0.0.0 --port 8432 --workers 4 --log-config "C:/website/logging.yaml"