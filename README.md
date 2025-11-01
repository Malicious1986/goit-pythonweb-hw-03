# goit-pythonweb-hw-03

goit-pythonweb-hw-03

## Local development

This repository uses environment variables for configuration. To run the project locally:

1. Copy the example env file and edit values if needed:

   ```sh
   cp .env.example .env
   # edit .env if you want to change PORT or STORAGE_PATH
   ```

2. Start services with Docker Compose:

   ```sh
   docker-compose up -d --build
   ```
