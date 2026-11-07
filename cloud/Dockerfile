# Nanban — cloud image (app only; the AI "brain" is a hosted model via API, so NO GPU needed).
# Build context must be the project root:  docker build -f cloud/Dockerfile -t nanban .
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NANBAN_LLM_BACKEND=hosted \
    NANBAN_WEB_COMPUTER_MODE=false \
    NANBAN_SECURITY_TAB=false \
    NANBAN_AUTOSTART_LAB=false \
    PORT=8000

WORKDIR /app

# git is handy for the in-app "update" button; everything else is pip wheels.
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# memory, documents and the doc index persist in these (mount volumes in compose / on the host)
VOLUME ["/app/data", "/app/documents"]

EXPOSE 8000

# server.py reads $PORT and binds 0.0.0.0; logins come from NANBAN_USERS (see .env.example)
CMD ["python", "server.py"]
