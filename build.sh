#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn --no-cache-dir

# Run Django migrations for both databases
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --database=default
python manage.py migrate --database=items

# Collect static files
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None"
