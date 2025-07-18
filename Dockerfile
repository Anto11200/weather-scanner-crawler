FROM python:3.12-alpine

ENV TZ=Europe/Rome

# Imposta la directory di lavoro all'interno del container
WORKDIR /workspace

# Aggiunge timezone (fuso orario corretto)
RUN apk add --no-cache tzdata
RUN cp /usr/share/zoneinfo/Europe/Rome /etc/localtime

COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copia tutti i file del progetto (inclusi gli script schedulati)
COPY . .

ENTRYPOINT [ "python", "app.py" ]