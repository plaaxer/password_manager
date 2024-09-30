
FROM python:latest


RUN apt-get update && \
    apt-get install -y postgresql postgresql-contrib && \
    apt-get clean

# you can change these environment variables to whatever you want, but make sure to change them in config.yaml as well
ENV POSTGRES_USER=pwmanager_user
ENV POSTGRES_PASSWORD=pwmanager_password
ENV POSTGRES_DB=password_manager

ENV PYTHONPATH /app

RUN mkdir -p /var/lib/postgresql/data

ENV PGDATA=/var/lib/postgresql/data

# changes authentication method inside container to trust for local connections
# security is not a concern here, given its isolated and local nature, as per https://www.postgresql.org/docs/current/auth-trust.html
RUN sed -i "s/local   all             all                                     peer/local   all             all                                     trust/g" /etc/postgresql/*/main/pg_hba.conf

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
