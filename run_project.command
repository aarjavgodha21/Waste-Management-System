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

source .venv/bin/activate

if python - <<'PY'
import importlib.util
mods = ("django", "MySQLdb", "PIL")
missing = [m for m in mods if importlib.util.find_spec(m) is None]
raise SystemExit(0 if not missing else 1)
PY
then
  echo "Python dependencies are already installed."
else
  python -m pip install --upgrade pip setuptools wheel
  python -m pip install -r requirements.txt
fi

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

for required_var in DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT; do
  if [ -z "${!required_var:-}" ]; then
    echo "Missing $required_var in waste_management/.env"
    exit 1
  fi
done

if ! mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"; then
  echo "Failed to connect to MySQL with values from waste_management/.env"
  echo "Check DB_USER, DB_PASSWORD, DB_HOST, and DB_PORT."
  exit 1
fi

cd waste_management
python manage.py migrate
exec python manage.py runserver
