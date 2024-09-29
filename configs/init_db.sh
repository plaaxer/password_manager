#!/bin/bash
# init_db.sh


service postgresql start

su postgres -c "psql --command \"CREATE USER $POSTGRES_USER WITH SUPERUSER PASSWORD '$POSTGRES_PASSWORD';\""
su postgres -c "createdb -O $POSTGRES_USER $POSTGRES_DB"

service postgresql stop