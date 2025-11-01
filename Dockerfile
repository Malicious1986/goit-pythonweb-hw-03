FROM python:3.11-slim

WORKDIR /app

ARG APP_PORT=3000
ENV PORT=${APP_PORT}
ENV STORAGE_PATH=/app/storage

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE ${PORT:-3000}

CMD ["python", "server.py"]
