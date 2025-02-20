# Bot Service (Expense Tracker API)

## Overview
This service is a FastAPI-based backend that processes user messages, extracts expense-related details, and stores them in a PostgreSQL database. It interacts with a Telegram bot (connector service) to provide automated expense tracking.

## Prerequisites
- **Python** (Version 3.13+ recommended)
- **Docker** (For containerized deployment)
- **A PostgreSQL database** (Managed via Docker Compose)
- **DeepSeek API Key** (For expense parsing)

## Setup Instructions

### 1. Clone the Repository
```sh
git clone <repository-url>
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory of the `bot_service` and add:
```sh
DATABASE_URL=postgresql://myuser:mypassword@db:5432/mydatabase
DEEPSEEK_API_KEY=<your-deepseek-api-key>
```
Ensure the `DATABASE_URL` matches the database service defined in your Docker Compose setup.

### 4. Running the Services with Docker Compose
Since this service relies on a PostgreSQL database and works with the Telegram bot connector, we use **Docker Compose** to orchestrate them.

#### Build and Start All Services
```sh
docker-compose up --build
```
This will:
- Start a **PostgreSQL database**
- Start the **bot service** (FastAPI backend)
- Start the **connector service** (Telegram bot)

#### Running Services in Detached Mode
To run the services in the background, use:
```sh
docker-compose up -d --build
```

#### Stopping the Services
To stop all running containers:
```sh
docker-compose down
```

## API Endpoints

### 1. Add a User to the Whitelist
```http
POST /add_user
```
#### Request Body:
```json
{
  "telegram_id": "12345678"
}
```
#### Response:
```json
{
  "status": "success",
  "message": "User added to whitelist"
}
```

### 2. Process a User Message
```http
POST /process_message
```
#### Request Body:
```json
{
  "telegram_id": "12345678",
  "message": "Spent 20 on food"
}
```
#### Response:
```json
{
  "status": "success",
  "data": {
    "category": "Food",
    "description": "food",
    "amount": 20.0
  }
}
```

## Logging
The service logs events and errors using Python’s logging module:
- Console output

## Troubleshooting
- Ensure the `.env` files are correctly configured for each service.
- Check logs using:
  ```sh
  docker-compose logs -f bot_service
  ```
- Ensure the database is running and accessible.
- Restart the services after making configuration changes.

