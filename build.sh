#!/bin/bash

# Create and activate virtual environment
python -m venv venv
. venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None"
