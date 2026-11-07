# Nanban Cloud (chat-only) — runs on Render, Railway, Fly.io, or any container host.
FROM python:3.12-slim

WORKDIR /app
COPY deploy/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# app_cloud.py reuses ui_theme.py from the repo root for the same look (optional).
COPY deploy/app_cloud.py ./app_cloud.py
COPY ui_theme.py ./ui_theme.py

ENV PORT=7860
EXPOSE 7860

# Set these at deploy time (dashboard env vars), never bake secrets into the image:
#   LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, APP_PASSWORD (optional)
CMD ["python", "app_cloud.py"]
