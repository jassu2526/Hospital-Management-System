#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (Whitenoise will serve them)
python manage.py collectstatic --no-input

# Run migrations to update database schema
python manage.py makemigrations
python manage.py migrate
