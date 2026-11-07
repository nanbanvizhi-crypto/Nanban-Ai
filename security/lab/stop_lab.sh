#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "Stopping the practice lab..."
docker compose down
echo "Done."
