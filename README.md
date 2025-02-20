# Darwin AI Challenge Repository

Welcome to the project repository for the Darwin AI challenge. This repository contains the necessary services and configurations to run the system locally using Docker Compose.

## Project Structure

```
.
├── bot_service
│   ├── db
│   │   ├── init.sql
│   ├── .env
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── README.md
│   ├── ...
├── connector_service
│   ├── src
│   │   ├── connector.ts
│   ├── .env
│   ├── dockerfile
│   ├── package.json
│   ├── README.md
│   ├── ...
├── .gitignore
├── docker-compose.yaml
```

## Running the Services

To run both the `bot_service`, `connector_service`, and the database concurrently, use Docker Compose:

```sh
docker-compose up --build
```

This command will:
- Start the AI chat bot service (`bot_service`)
- Start the connector service (`connector_service`)
- Start the database with the necessary schema

For more details on each service, refer to their respective `README.md` files:
- [`bot_service/README.md`](bot_service/README.md)
- [`connector_service/README.md`](connector_service/README.md)

## Future Improvements

- **Unit Testing**: Implement unit tests using `pytest`, including mocking AI chat responses and database interactions.
- **Hexagonal Architecture**: Given that the service primarily consists of integrations, restructuring the project using a hexagonal architecture to better abstract LLM logic and dependencies.
- **Improved Logging & Monitoring**: Implement structured logging and monitoring to enhance observability.
- **Security Enhancements**: Strengthening environment variable handling, authentication, and authorization mechanisms.


