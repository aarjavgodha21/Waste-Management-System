#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

if [ ! -d ".venv" ]; then
  if command -v python3.12 >/dev/null 2>&1; then
    python3.12 -m venv .venv
  else
    python3 -m venv .venv
  fi
fi

if [ ! -x ".venv/bin/python" ]; then
  rm -rf .venv
  if command -v python3.12 >/dev/null 2>&1; then
    python3.12 -m venv .venv
  else
    python3 -m venv .venv
  fi
fi

PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"

if "$PYTHON_BIN" - <<'PY'
import importlib.util
mods = ("django", "MySQLdb", "PIL")
missing = [m for m in mods if importlib.util.find_spec(m) is None]
raise SystemExit(0 if not missing else 1)
PY
then
  echo "Python dependencies are already installed."
else
  "$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
  "$PYTHON_BIN" -m pip install -r requirements.txt
fi

# Ensure Homebrew and mysql CLI are on the PATH
for d in /opt/homebrew/bin /opt/homebrew/opt/mysql@8.4/bin /opt/homebrew/opt/mysql-client/bin /usr/local/opt/mysql@8.4/bin /usr/local/bin; do
  if [ -d "$d" ]; then
    export PATH="$d:$PATH"
  fi
done

if command -v brew >/dev/null 2>&1; then
  brew services start mysql@8.4 >/dev/null 2>&1 || true
fi

if [ ! -f "waste_management/.env" ]; then
  echo "Missing waste_management/.env"
  echo "Copy waste_management/.env.example to waste_management/.env and set DB_PASSWORD."
  exit 1
fi

# Load DB settings from waste_management/.env only.
set -a
source waste_management/.env
set +a

for required_var in DB_NAME DB_USER DB_HOST DB_PORT; do
  if [ -z "${!required_var:-}" ]; then
    echo "Missing $required_var in waste_management/.env"
    exit 1
  fi
done

MYSQL_AUTH_ARGS=("--protocol=TCP" "-h" "$DB_HOST" "-P" "$DB_PORT" "-u" "$DB_USER")
if [ -n "${DB_PASSWORD:-}" ]; then
  MYSQL_AUTH_ARGS+=("-p$DB_PASSWORD")
fi

if ! mysql "${MYSQL_AUTH_ARGS[@]}" -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"; then
  echo "Failed to connect to MySQL with values from waste_management/.env"
  echo "Check DB_USER, DB_PASSWORD, DB_HOST, and DB_PORT."
  exit 1
fi

cd waste_management
"$PYTHON_BIN" manage.py migrate

if "$PYTHON_BIN" - <<'PY'
from waste.models import products
raise SystemExit(0 if products.objects.exists() else 1)
PY
then
  echo "Demo data already present."
else
  "$PYTHON_BIN" manage.py seed_data
fi

# Kill any existing process on port 8000 so re-runs don't fail
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

exec "$PYTHON_BIN" manage.py runserver
