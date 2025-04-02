# django-fastapi

# Project Setup and Usage Guide

## Prerequisites

### Install `make` on Linux / macOS

#### Linux (Debian/Ubuntu-based):

```bash
sudo apt update && sudo apt install -y make
```

#### macOS (Using Homebrew):

```bash
brew install make
```

### Install Docker and Docker Compose

#### Linux (Debian/Ubuntu-based):

```bash
sudo apt update && sudo apt install -y docker.io docker-compose
```

#### macOS (Using Homebrew):

```bash
brew install docker docker-compose
```

Ensure that the Docker daemon is running before proceeding.

---

## Project Setup (Local)

### 1. Create `.env` File

Create a `.env` file in the root directory near `docker-compose.local.yml` and add the following environment variables:

```env
POSTGRES_USER=<POSTGRES_USER>
POSTGRES_PASSWORD=<POSTGRES_PASSWORD>
POSTGRES_DB=<POSTGRES_DB>
RABBITMQ_DEFAULT_USER=<RABBITMQ_DEFAULT_USER>
RABBITMQ_DEFAULT_PASS=<RABBITMQ_DEFAULT_PASS>
```

### 2. Create Backend Configuration File

Create a `.env` file in the `backend` directory (near `Makefile`) with the following configuration: </br>
Generate a secret key for `AUTHENTICATION__ACCESS_TOKEN__SECRET_KEY` using the following command:

```bash
python3 -c "import secrets; print(f'AUTHENTICATION__ACCESS_TOKEN__SECRET_KEY={secrets.token_hex(32)}')"
python3 -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"
```

```env
DEBUG=True
STATE=local
SECRET_KEY=<DJANGO_SECRET_EKY>
DATABASE__URI=postgres://<POSTGRES_USER>:<POSTGRES_PASSWORD>@localhost:5432/<POSTGRES_DB>
BROKER__URI=amqp://<RABBITMQ_DEFAULT_USER>:<RABBITMQ_DEFAULT_PASS>@localhost/
AUTHENTICATION__ACCESS_TOKEN__SECRET_KEY=<AUTHENTICATION__ACCESS_TOKEN__SECRET_KEY>
```

### 3. Create Worker Instagram

Create a `.env` file `/workers/instagram/.env` near their respective `Makefile`:

```env
RMQ_URI=amqp://<RABBITMQ_DEFAULT_USER>:<RABBITMQ_DEFAULT_USER>@localhost:5672
```

### 3. Create TGBot

Create a `.env` file `/bot/.env` near their respective `Makefile`:

```env
RMQ_URI=amqp://<RABBITMQ_DEFAULT_USER>:<RABBITMQ_DEFAULT_USER>@localhost:5672
TELEGRAM_BOT_TOKEN=<TELEGRAM_BOT_TOKEN>
```

---

## Running the Project Locally

### 1. Start Required Services

Run the following command to start the required services (PostgreSQL, RabbitMQ, etc.):

```bash
docker compose -f docker-compose.local.yml up -d
```

### 2. Setup Project Components

Run the following command to set up all required dependencies:

```bash
make setup-local
make start-local
```

### 3. Start Backend Locally

```bash
make start-local
```

### 4. Start Workers

Run next commands:

```bash
make setup-local
make start
```

## Project Setup (Dev)

### Create Configuration Files `.env`

Create a `.env` file in the root directory near `docker-compose.dev.yml` and add the following environment variables:

```env
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_DB=<your_database_name>
RABBITMQ_DEFAULT_USER=<your_rabbitmq_user>
RABBITMQ_DEFAULT_PASS=<your_rabbitmq_password>

TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>


BACKEND__DEBUG=False
BACKEND__STATE=prod
BACKEND__TCP_PORT=8200
BACKEND__SECRET_KEY=<your_backend_secret_key>
BACKEND__AUTHENTICATION_ACCESS_TOKEN_SECRET_KEY=<your_authentication_secret_key>
```

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

## Additional Commands

- **Stop all services**:
  ```bash
  docker compose -f docker-compose.local.yml down
  ```
- **Create admin in `backend` app**:
  ```bash
  docker compose -f docker-compose.dev.yml exec backend make create-admin
  ```
- **Check logs for multiple services (backend, rabbitmq, postgres)**:
  ```bash
  docker compose -f docker-compose.local.yml logs -f backend rabbitmq postgres
  ```

## Endpoints Documentation

### Swagger UI

http://localhost:8200/docs

### Admin panel

http://localhost:8200/admin

