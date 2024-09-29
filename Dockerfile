
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

COPY . /app
WORKDIR /app

RUN ls -R /app

RUN chmod +x /app/configs/init_db.sh
RUN /app/configs/init_db.sh

RUN pip install psycopg2
RUN pip install argon2-cffi
RUN pip install cryptography
RUN pip install pyyaml


CMD ["bash", "-c", "service postgresql start && python main.py"]
