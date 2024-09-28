
FROM python:latest


RUN apt-get update && \
    apt-get install -y postgresql postgresql-contrib && \
    apt-get clean


ENV POSTGRES_USER=plaxer
ENV POSTGRES_PASSWORD=a
ENV POSTGRES_DB=password_manager

ENV PYTHONPATH /app


RUN mkdir -p /var/lib/postgresql/data


ENV PGDATA=/var/lib/postgresql/data


COPY init_db.sh /init_db.sh
COPY main.py /app/main.py
COPY src /app/src
COPY config.yaml /app/config.yaml


RUN chmod +x /init_db.sh


WORKDIR /app

RUN pip install psycopg2
RUN pip install argon2-cffi
RUN pip install cryptography
RUN pip install pyyaml


RUN /init_db.sh

RUN ls -R /app

CMD ["bash", "-c", "service postgresql start && python main.py"]
