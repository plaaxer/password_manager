import psycopg2
import sys
import src.aux as aux

class Communicator:
    def __init__(self):

        # default connection
        self.conn_params = aux.get_conn_params()

         # connects to postgresql database
        self.cursor = self.connect()
    
    def connect(self) -> psycopg2.extensions.cursor:

        try:
            conn = psycopg2.connect(**self.conn_params)
            conn.autocommit = True
            cur = conn.cursor()
            print("Connected to PostgreSQL database.")
            return cur
        
        except psycopg2.Error as e: # failed connection, maybe no user yet
            print("\nError while connecting to PostgreSQL:", e)
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
            self.cursor.execute(f"DELETE FROM stashes_info.stashes WHERE stash_name = '{name}'")
            print(f"Stash {name} dropped successfully.")

        except psycopg2.Error as e:
            print(f"Error dropping schema {name}: {e}")
    
    # adds a stash to the stashes table
    def add_stash_info(self, name: str, master_key_hash: str) -> None:

        try:
            self.cursor.execute(f"INSERT INTO stashes_info.stashes (stash_name) VALUES ('{name}')")
            self.cursor.execute(f"UPDATE stashes_info.stashes SET master_key_hash = '{master_key_hash}' WHERE stash_name = '{name}'")
        
        except psycopg2.Error as e:
            print(f"Error adding stash info: {e}")
    
    # creates the passwords table for a given stash
    def create_password_table(self, name: str) -> None:

        try:
            self.cursor.execute(f"CREATE TABLE {name}.passwords (id SERIAL PRIMARY KEY, service TEXT UNIQUE, hashed_username TEXT, hashed_password TEXT)")
        
        except psycopg2.Error as e:
            print(f"Error creating passwords table: {e}")
    
    def get_master_key_hash(self, name: str) -> str:

        #returns the master key hash from the info table of the given schema
        try:
            self.cursor.execute(f"SELECT master_key_hash FROM stashes_info.stashes WHERE stash_name = '{name}'")
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
    
    def list_stashes(self) -> None:
            
        try:
            self.cursor.execute("SELECT stash_name FROM stashes_info.stashes WHERE stash_name != 'public' AND stash_name != 'information_schema'")
            stashes = self.cursor.fetchall()
            print("Stashes:")
            for stash in stashes:
                print(stash[0])
            
        except psycopg2.Error as e:
            print(f"Error listing stashes: {e}")