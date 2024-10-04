# Password Manager

- A fully functional and secure password manager made using Python, PostgreSQL, Cryptography, Argon2, and Docker.

## Features

- **Encryption & Decryption**: Secured with randomly generated salts and a master-password.
- **Fast Data Retrieval**: Quickly retrieve data from the PostgreSQL database.
- **Command-Line Application**: Includes multiple terminal commands for easy management.

## Table of Contents

- [Setup](#setup)
- [Encryption](#encryption)
- [Usage](#usage)
- [Example](#example)

## Setup

### Docker Installation
This application requires docker installed in your computer. It eases setup as there is no other requirement and you can run this in any OS (as long as it supports Docker). To install it in Debian distros, run: 

      sudo apt-get update
      sudo apt-get install docker.io

Check installation by either checking version or by running default container:

      docker --version
      docker run hello-world

### Running

First, be sure that you are located at /password_manager. Then, run:

      docker build -t password_manager .

You can change the name password_manager to whatever you like. When it finishes building, run the app doing:

      docker run -it password_manager

**ATTENTION:** Do not remove or delete the running container without the backup of data, as it will be lost. It is not recommended to change the config.yaml file, but if you do, you'll have to rebuild the image for it to take effect (database data is not mantained.)

## Encryption

- The stored passwords and usernames are encrypted utilizing symmetric-key encryption and authentication based on the chosen master-password. That means that the master-password must, naturally, be kept safe from third parties, otherwise data could be stolen, but it also means that it is virtually impossible to retrieve data without it.

- The specific tool for encryption and decryption utilized in the password manager is Fernet, a tool for symmetric encryption available on python’s Cryptography module, developed by Python Cryptographic Authority (PYCA).

- To generate a Fernet object, however, it is needed a URL-safe base64-encoded 32-byte key, meaning that most (if not all) master-passwords are unfit for being a key directly. To solve that, we first run the master-password through a key-derivation function (KDF), in this case, PBKDF2HMAC, also available on the Cryptography module.

- The PBKDF2HMAC algorithm receives as parameters a SHA256 hashing function, number of iterations and length, but most importantly a randomly (as random as it gets, os.urandom) generated salt. This salt is extremely important as it will be unique for each added password on the database - meaning that if you have the same password on multiple websites (not advisable), to an attacker all encrypted data will differ even though the passwords are the same. It also makes it so that the database is significantly stronger against rainbow table attacks.

- The salt is then appended to the encrypted data, which is then stored in the database. When retrieving it, the master_password is used to generate the same Fernet object; this time, however, with the salt that is extracted from the last bytes. Having the salt exposed is naturally not a problem, as one can only generate the Fernet object with the correct master-password.

## Usage

- The password manager works using stashes; consider them collections of passwords. Most users won't need more than one, but if you do, it's a working feature. Each stash has its own unique master password, used to encrypt and decrypt data, and refers to a single schema each in the PostgreSQL database (present in the same container). As always, -h flag gives helpful tips and useful commands.

- To register a master password (create a stash):

      --register/-r [stash_name]
      --register/-r
    If [stash_name] is not given, it defaults to the config.yaml default_stash variable. It will prompt you for the master password you want to register.

- To enter a stash, you have multiple options, such as:

        --enter/-e [stash_name] [master_password]

        --enter/-e [master_password]

        --enter/-e [stash_name] -gs

        [master_password]
        
        [stash_name] -gs

    When [stash_name] is not given, it defaults to the one set at the config.yaml file. When [master_password] is not given, it is prompted (more secure). Easiest way to login is to just [master_password].
- To add a password (you have entered a stash):

      --add/-a [service] [user] [password] 

- To get a password:

      --get/-g [service]

## Example
- Suppose you will only use the default stash and want to add user linux@gmail.com, with password 123, for service OpenSource, and then retrieve said passowrd and user. You do:

        Enter command: -r
        Enter master key: secret_masterpassword
        Confirm master key: secret_masterpassoword

        Enter command: -e secret_masterpassword
        Enter command: -a OpenSource linux@gmail.com 123
        Enter command: -g OpenSource
