#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files with --clear flag to ensure clean collection
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

# Remove the development server start command for production
# python manage.py runserver
