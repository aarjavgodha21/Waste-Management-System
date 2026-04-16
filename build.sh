#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Navigating to project directory..."
cd waste_management

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Applying database migrations..."
python manage.py migrate --no-input

echo "Seeding initial e-waste database records..."
python manage.py seed_data

echo "Build complete."
