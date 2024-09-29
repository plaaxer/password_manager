# Password Manager

- A completely functional and secure password manager made using python and postgresql. 

- **Features:** encryption and decryption with randomly generated salt through a master-password, quick retrieval of data from database, terminal-based application with multiple commands. More detail on cryptography below.

## Setup

- **Dependencies:** python3, postgresql, psycopg2, argon2

- **Postgresql setup:** the password manager requires access to a postgresql user to create the default database where the passwords are stored. 

- If you are familiar with postgresql and **already have a user/database you´d like to use** for the password_manager:

If you have both the database and user ready, change the "active_status"  parameter on configs/config.yaml to true. This will prevent the program of creating a new database for the passwords. And change the connection parameters in the same file. Alternatively, if you have only the user, but not a database yet, just change the connection_parameters and the program will automatically create a database for you. If you wish to change its name, change it on the "default_database_name" parameter.

- You **are not familiar** with postgresql and have just installed it:

Run ./create_user.sh to create the postgresql user that has the same name as you (otherwise customize connection on the yaml file and change authentication to password and not peer instead). Then change user on "conn_params" (also configs/config.yaml) to your OS username (has to be the same as the recently created postgresql user). Run app. When connecting, it will prompt for your postgresql user password (the one that you've created just now). It automatically detects that there's no database for the password_manager yet and creates one. It also changes the connection parameters to the newly created database, so no need to do that.

## Encryption

- The stored passwords and usernames are encrypted utilizing symmetric-key encryption and authentication based on the chosen master-password. That means that the master-password must, naturally, be kept safe from third parties, otherwise data could be stolen, but it also means that it is virtually impossible to retrieve data without it.

- The specific tool for encryption and decryption utilized in the password manager is Fernet, a tool for symmetric encryption available on python’s Cryptography module, developed by Python Cryptographic Authority (PYCA).

- To generate a Fernet object, however, it is needed a URL-safe base64-encoded 32-byte key, meaning that most (if not all) master-passwords are unfit for being a key directly. To solve that, we first run the master-password through a key-derivation function (KDF), in this case, PBKDF2HMAC, also available on the Cryptography module.

- The PBKDF2HMAC algorithm receives as parameters a SHA256 hashing function, number of iterations and length, but most importantly a randomly (pseudo) generated salt. This salt is extremely important as it will be unique for each added password on the database - meaning that if you have the same password on multiple websites (not advisable), to an attacker all encrypted data will differ even though the passwords are the same. It also makes it so that the database is significantly stronger against rainbow table attacks.

- The salt is then appended to the encrypted data, which is then stored in the database. When retrieving it, the master_password is used to generate the same Fernet object; this time, however, with the salt that is extracted from the last bytes. Having the salt exposed is naturally not a problem, as one can only generate the Fernet object with the correct master-password.
