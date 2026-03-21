# Development Plan for LMS Telegram Bot

This document outlines the plan for developing the LMS Telegram Bot. The development is divided into several tasks, from scaffolding the project to deployment.

## Task 1: Plan and Scaffold

The first step is to create a solid project structure. This includes:

- **Project Skeleton**: Create the main directory `bot/` with subdirectories `handlers/` and `services/`.
- **Entry Point**: Implement `bot/bot.py` which will handle both starting the bot for Telegram and a `--test` mode for offline command testing. This is crucial for P0.2.
- **Handlers**: The `handlers/` directory will contain the logic for each bot command, designed to be testable without any dependency on the Telegram API, fulfilling P0.1.
- **Configuration**: A `config.py` file will be used to load environment variables like API keys and base URLs from a `.env.bot.secret` file.
- **Dependencies**: All Python dependencies will be managed in `bot/pyproject.toml` using `uv`.

## Task 2: Backend Integration

With the scaffold in place, the next task is to integrate with the LMS backend.

- **API Client**: A client for the LMS API will be implemented in the `services/` directory. This client will handle requests to endpoints for health checks, labs, and scores.
- **Handlers Implementation**: The placeholder handlers from Task 1 will be updated to use the API client to fetch real data. For example, `/health` will call the backend's health check endpoint.

## Task 3: Intent Routing and LLM

This task focuses on making the bot smarter using a Large Language Model (LLM).

- **Intent Routing**: Instead of simple command matching, the bot will use an LLM to understand natural language queries and route them to the appropriate handler. For example, "what labs are available" should be routed to the `/labs` handler.
- **LLM Client**: A client for the LLM API will be implemented in `services/`.

## Task 4: Deployment

The final step is to ensure the bot is deployed and running reliably on the VM.

- **Dockerfile**: A `Dockerfile` will be created for the bot to containerize it.
- **Docker Compose**: The `docker-compose.yml` will be updated to include the bot service.
- **CI/CD**: A GitHub Actions workflow will be set up to automatically deploy the bot on push to the `main` branch. This will involve pulling the latest code, rebuilding the Docker image, and restarting the service.
- **Monitoring**: The `nohup` and logging setup will be used for basic monitoring.

This plan ensures a modular, testable, and scalable architecture for the bot.
