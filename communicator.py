import psycopg2
import sys
import aux

class Communicator:
    def __init__(self):

        # default connection, change according to needs on config file
        self.conn_params = aux.get_conn_params()

        db_password = input(f"Enter database password for user {self.conn_params['user']}: ")

         # connects to postgresql database
        self.cursor = self.connect(db_password)

        # if first time running, create default database
        if not aux.get_active_status():
            self.create_default_database()
    
    def connect(self, db_password: str) -> psycopg2.extensions.cursor:

        try:
            conn = psycopg2.connect(**self.conn_params, password=db_password)
            conn.autocommit = True
            cur = conn.cursor()
            print("Connected to PostgreSQL database.")
            return cur
        
        except psycopg2.Error as e: # failed connection, maybe no user yet
            print("\nError while connecting to PostgreSQL:", e)
            print(aux.info_no_database)
            sys.exit(1)
    
    def create_stash(self, name: str) -> None:

        try:
            # schema = stash
            self.cursor.execute(f"CREATE SCHEMA {name}")
            print(f"Stash {name} created successfully.")

        except psycopg2.Error as e:
            print(f"Error creating schema {name}: {e}")

    def drop_stash(self, name: str) -> None:

        try:
            self.cursor.execute(f"DROP SCHEMA {name} CASCADE")
            print(f"Stash {name} dropped successfully.")

        except psycopg2.Error as e:
            print(f"Error dropping schema {name}: {e}")

    def create_info_table(self, name: str, master_key_hash: str) -> None:

        try:
            self.cursor.execute(f"CREATE TABLE {name}.info (master_key_hash TEXT)")
            self.cursor.execute(f"INSERT INTO {name}.info VALUES ('{master_key_hash}')")
        
        except psycopg2.Error as e:
            print(f"Error creating info table: {e}")
    
    def create_password_table(self, name: str) -> None:

        try:
            self.cursor.execute(f"CREATE TABLE {name}.passwords (id SERIAL PRIMARY KEY, service TEXT UNIQUE, hashed_username TEXT, hashed_password TEXT)")
        
        except psycopg2.Error as e:
            print(f"Error creating passwords table: {e}")

    def create_default_database(self) -> None:

        print(f"Creating default database: {aux.get_options()['default_database_name']}")
        # ìndicates that a database is already in use
        aux.set_active_status(True)
        # sql query
        self.cursor.execute(f"CREATE DATABASE {aux.get_options()['default_database_name']}")
        # change default database parameter to the one just created
        aux.set_dbname(aux.get_options()['default_database_name'])
    

    def get_master_key_hash(self, name: str) -> str:

        #returns the master key hash from the info table of the given schema
        try:
            self.cursor.execute(f"SELECT master_key_hash FROM {name}.info")
            return self.cursor.fetchone()[0]
        
        except psycopg2.Error as e:
            print(f"Error authenticating: {e}")
            return False
        
    def store_password(self, name: str, service: str, username: str, password: str) -> None:

        try:
            query = f"""
            INSERT INTO {name}.passwords (service, hashed_username, hashed_password)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (service, username, password))
            print(f"Password for {service} stored successfully.")
        
        except psycopg2.Error as e:
            print(f"Error storing password: {e}")

    def retrieve_password(self, name: str, service: str) -> tuple:

        try:
            self.cursor.execute(f"SELECT * FROM {name}.passwords WHERE service = '{service}'")
            result = self.cursor.fetchone()

            if result:
                return (result[2],result[3])
            else:
                print(f"Service {service} not found.")
        
        except psycopg2.Error as e:
            print(f"Error retrieving password: {e}")