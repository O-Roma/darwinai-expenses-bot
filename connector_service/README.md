# Telegram Bot Connector Service

## Overview
This service is a Telegram bot that helps users track their expenses by interacting with a backend service. The bot processes user messages and sends the relevant data to the backend for categorization and storage.

## Prerequisites
- **Node.js** (Version 16+ recommended)
- **Docker** (For containerized deployment)
- **A valid Telegram Bot Token** (Obtained from [BotFather](https://t.me/BotFather))

## Setup Instructions

### 1. Clone the Repository
```sh
git clone <repository-url>
```

### 2. Install Dependencies
```sh
npm install
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add the required variables:
```sh
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
BOT_SERVICE_URL=http://bot_service:8000/process_message
```
Ensure the `BOT_SERVICE_URL` matches the service name defined in your Docker network.

### 4. Running the Services with Docker Compose
Since the project consists of multiple services, including a database, we use **Docker Compose** to orchestrate them.

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

## Logging
The bot logs events and errors using Winston:
- Console output (for real-time logs)
- `bot.log` file (for persistent logs)

## Stopping the Bot
If running locally:
```sh
CTRL+C
```
If running via Docker:
```sh
docker stop <container-id>
```

## Troubleshooting
- Ensure the `.env` file is correctly configured.
- Check logs (`bot.log` or Docker logs) for error messages.
- Ensure the backend service (`bot_service`) is reachable from the bot.
- Restart the bot after making configuration changes.

