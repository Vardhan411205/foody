#!/bin/bash

# Ensure Python 3.12 is being used
eval "$(pyenv init -)"
pyenv install -s 3.12.6
pyenv global 3.12.6
python --version

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn==21.2.0 --no-cache-dir

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Clear existing staticfiles
rm -rf staticfiles/*

# Collect static files with clear
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

# Print installed packages for debugging
pip freeze
