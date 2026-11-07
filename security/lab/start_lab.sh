#!/usr/bin/env bash
# Nanban Security Lab — local practice only (Linux / Mac / WSL)
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "   Nanban Security Lab  -  local practice only"
echo "============================================"

if ! command -v docker >/dev/null 2>&1; then
  echo "[X] Docker is not installed. Install Docker, then run this again."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "[X] Docker is not running. Start the Docker service/app and try again."
  exit 1
fi

echo "Starting the practice targets (first time downloads a few GB)..."
docker compose up -d

cat <<'EOF'

============================================
   Lab is running on THIS computer only:

   DVWA        http://127.0.0.1:8080   (login: admin / password)
   Mutillidae  http://127.0.0.1:8082   |  bWAPP  http://127.0.0.1:8083/install.php
   VAmPI(API)  http://127.0.0.1:5001    |  DVGA   http://127.0.0.1:5013
   Juice Shop  http://127.0.0.1:3000
   WebGoat     http://127.0.0.1:8081/WebGoat

   These are the ONLY systems you may attack.
   Stop the lab anytime with:  ./stop_lab.sh  (or docker compose down)
============================================
EOF
