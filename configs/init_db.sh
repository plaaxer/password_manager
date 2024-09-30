#!/bin/bash
# init_db.sh


service postgresql start

su postgres -c "psql --command \"CREATE USER $POSTGRES_USER WITH SUPERUSER PASSWORD '$POSTGRES_PASSWORD';\""
su postgres -c "createdb -O $POSTGRES_USER $POSTGRES_DB"
su postgres -c "psql -U $POSTGRES_USER -d $POSTGRES_DB -c \"CREATE SCHEMA IF NOT EXISTS stashes_info;\""
su postgres -c "psql -U $POSTGRES_USER -d $POSTGRES_DB -c \"CREATE TABLE IF NOT EXISTS stashes_info.stashes (
    stash_name TEXT PRIMARY KEY,
    master_key_hash TEXT
);\""

service postgresql stop