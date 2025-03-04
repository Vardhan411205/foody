#!/bin/bash

# Redirect stderr to suppress tput errors
exec 2>/dev/null

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Clear existing staticfiles
rm -rf staticfiles/*

# Collect static files with clear
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
