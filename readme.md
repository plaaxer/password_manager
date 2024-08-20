Master-password encryption: argon2.
Database encryption: ed25519.

https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
https://en.wikipedia.org/wiki/EdDSA#Ed25519
https://github.com/hynek/argon2-cffi/blob/main/docs/argon2.md
https://stackoverflow.com/questions/58431973/argon2-library-that-hashes-passwords-without-a-secret-and-with-a-random-salt-tha
https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/
https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange

ideas:
i need a way for the master_password to both encrypt and decrypt the database. maybe I could generate a symmetric or assymetric key to encrypt the data; add it to the database; and then decrypt it.

https://cryptography.io/en/latest/fernet/#cryptography.fernet.Fernet --> fernet; symmetric encryption and decryption of data put into the database.

https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC --> key derivation function to be used with the fernet.

so, basically, I cannot block the access to the PostgreSQL database in such a way that only the selected user can access, as whomever has root should and is able to access each and every database on the host machine, as per the natural and fundamental working of PSQL.

I, however, still want to store data in some sort of database and not in plain text, and it's is not like root access should be given in a easy way. Obviously, the database content will be encrypted prior to being added; it is just for a second layer of security (albeit weak) to be added.

Therefore, I've decided to proceed with the implementation of a PostgreSQL database. In future projects I can also take a look at docker or at some kind of container. That's, however, for the future.

REQUIREMENTS:

argon2
postgresql
python3
psycopg2

obs: please ajust the communicator.py default pw if you have changed it and it is not 'postgres'. An access to postgresql is required to create the databases for each "account"/"key".

if you do not wish to grant access of the postgres user to the program, you can also create a specific role that enables creating of databases and use it to create databases instead.

daí, eu posso fazer que, caso for a primeira vez da pessoa utilizando o app, roda um script de bash, que pede permissao para criar esse user/superuser que servirá para criar as demais databases. seria bem legal. os sudos seriam preenchidos pela pessoa.