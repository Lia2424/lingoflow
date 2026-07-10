#!/usr/bin/env bash
# Weekly incremental YouTube ingest for LingoFlow.
#
# Local dev only — expects backend/.venv. For Docker prod, run inside the
# container: python -m scripts.weekly_ingest
#
# Usage:
#   ./scripts/weekly_ingest.sh
#
# Local cron (Sundays 9am) — does NOT run when the app is deployed elsewhere:
#   crontab -e
#   0 9 * * 0 /path/to/LingoFlow/backend/scripts/weekly_ingest.sh >> /tmp/lingoflow-ingest.log 2>&1
#
# Deploy scheduling → see CONTENT_INGESTION.md ("Scheduling when you deploy").

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${BACKEND_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON}" ]]; then
  echo "error: ${PYTHON} not found — create venv and install deps first" >&2
  exit 1
fi

cd "${BACKEND_DIR}"
exec "${PYTHON}" -m scripts.weekly_ingest
