#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create the 6 app users (skips if already exist)
python manage.py create_initial_users

# Auto-create superuser from environment variables (skips if already exists)
python manage.py createsuperuser --no-input || true
