#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create all 7 users including admin (skips if already exist)
python manage.py create_initial_users

# Run backfill to populate in-progress & done states for existing reports
# python manage.py backfill_in_progress
