# Argus Password Manager

Argus is a secure-by-design password management system built with a client-server architecture. It utilizes Python, FastAPI, and PostgreSQL, fully containerized with Docker for ease of deployment.
The name Argus comes from [Argus Panoptes](https://en.wikipedia.org/wiki/Argus_Panoptes), the all-seeing giant in Greek mythology.

---

## Architecture and Security Notice
While all data is stored encrypted in the database, the plain text password must be sent to the server for the encryption/decryption process to occur. Because the server "sees" the secret during transit and processing:

- **Intended Use**: This application is currently designed to be run locally or within a trusted private network.

- **Trust Model**: The user must trust the host server and the integrity of the transit layer (HTTPS).


**IMPORTANT**: Do NOT run this version in a remote server without secure HTTPS connections. It will be vulnerable to MITM and other attacks.

---

## Technical Features

- **Robust Encryption**: Stored credentials are encrypted using the Fernet algorithm (AES-128 in CBC mode with HMAC authentication).

- **Key Derivation**: Master passwords are processed through PBKDF2HMAC with unique, per-entry salts to generate encryption keys.

- **Asynchronous API**: Built with FastAPI for high-performance, non-blocking database operations.

- **JWT Authentication**: Implements stateless JSON Web Tokens for secure user sessions.

---

## Setup

Getting your own secure password manager instance running is simple.

### Prerequisites

- **Docker & Docker Compose:**  
    This application requires Docker to be installed. The setup script will handle the rest.  
    [Install Docker here.](https://docs.docker.com/get-docker/)

---

### Running the Application

**Clone the Repository:**
```sh
git clone git@github.com:plaaxer/argus_password_manager.git
cd argus_password_manager
```

**Run the Setup Script**  
This script will create a `.env` file with a unique, secure `SECRET_KEY` for token authentication and then launch the application.

- **For Linux or macOS:**
        ```sh
        bash setup.sh
        ```

- **For Windows (manual setup):**
        1. Copy the `.env.example` file and rename it to `.env`.
        2. Open PowerShell and run:
                ```sh
                openssl rand -hex 32
                ```
                (if you have OpenSSL installed) or use another method to generate a secure random string.
        3. Paste this string as the value for `SECRET_KEY` in your `.env` file.
        4. Run:
                ```sh
                docker compose up --build
                ```

> The first time you run this, it may take a minute or so to download the Docker images and build the backend container.

---

## Usage

Once the setup is complete, the backend API will be running and accessible.

### Interactive API Documentation (Swagger UI)

The best way to interact with your API is through the built-in documentation.

- Open your web browser and navigate to:  
    [http://localhost:8000/docs](http://localhost:8000/docs)

From this page, you can:

- **Register a new user:**  
    Use the `POST /api/v1/register` endpoint.

- **Log in:**  
    Use the `POST /api/v1/token` endpoint. The Swagger UI provides a green "Authorize" button at the top-right that makes it easy to log in and automatically apply your token to all subsequent requests.

- **Store, retrieve, update, and delete your passwords** using the protected `/api/v1/passwords` endpoints.

---

## Encryption Model Detail

- **Database**: All sensitive fields (encrypted_username, encrypted_password) are stored as Base64 encoded blobs.
- **Salt**:  A unique salt is generated for every entry and appended to the ciphertext. This ensures that even identical passwords result in completely different stored strings, preventing rainbow-table attacks.
- **Master Password**: The server does not store your master password. It is used only in-memory during a request to derive the transient encryption key required to unlock your stash.

---