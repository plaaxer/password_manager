

-- Create the schema for your application
CREATE SCHEMA IF NOT EXISTS stashes_info;

-- Create the stashes table within that schema
CREATE TABLE IF NOT EXISTS stashes_info.stashes (
    stash_name TEXT PRIMARY KEY,
    master_key_hash TEXT NOT NULL
);