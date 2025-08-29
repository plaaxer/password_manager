# Argus Password Manager

A fully functional and secure password manager built on a modern client-server architecture. The backend is powered by **Python**, **Cryptography**, **FastAPI**, and **PostgreSQL**, all containerized with **Docker** for easy setup and deployment.

The name Argus comes from [Argus Panoptes](https://en.wikipedia.org/wiki/Argus_Panoptes), the all-seeing giant in Greek mythology.

---

## What's New in v2.0.0

This is a complete architectural rewrite of the original Password Manager.

- **Backend API:**  
    The command-line interface has been replaced with a robust, stateless RESTful API built with FastAPI.

- **Client-Server Model:**  
    The application is now split into a backend (which you can host remotely) and a future frontend, allowing for greater flexibility.

- **Standardized Authentication:**  
    Implements JWT (JSON Web Token) for secure, stateless authentication.

- **Simplified Setup:**  
    A single script and docker compose are all you need to get a full environment running.

---

## Features

- **Zero-Knowledge Encryption:**  
    All usernames and passwords are encrypted using a key derived from your master password. The server never stores the master password, ensuring only you can decrypt your data.

- **Modern Tech Stack:**  
    Utilizes FastAPI for high-performance asynchronous API endpoints, PostgreSQL for reliable data storage, and Argon2 for secure password hashing.

- **Dockerized Environment:**  
    The entire backend and database are containerized, ensuring a consistent and easy-to-manage setup on any OS that supports Docker.

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

## Encryption Model

The core zero-knowledge encryption model from v1.0.0 remains.

- The stored passwords and service usernames are encrypted utilizing symmetric-key encryption (**Fernet**) based on your chosen master password.
- To make the master password suitable for encryption, it is first run through a key-derivation function (**PBKDF2HMAC**) with a unique, randomly generated salt for each password entry.
- This means that even if an attacker gained access to the database, they could not decrypt your data without your master password. The server never knows your master password; it is only sent temporarily over a secure connection to perform on-the-fly decryption for a single request.

---