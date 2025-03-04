#!/usr/bin/env bash

# Prevent tput errors by forcing non-interactive mode
export TERM=dumb
export CI=true
export NONINTERACTIVE=1

# Exit on error
set -o errexit

# Redirect stderr to suppress tput errors
exec 2>/dev/null

# Debugging information
echo "Starting build process..."
echo "Working directory: $(pwd)"

# Disable all color output and terminal features
export NO_COLOR=1
export PYTHONWARNINGS=ignore
export PYTHONUNBUFFERED=1

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Python upgrade and setup
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Django commands
echo "Running Django commands..."

# Collect static files
echo "Collecting static files..."
rm -rf staticfiles/*
python manage.py collectstatic --noinput

# Run migrations for both databases
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --database=default
python manage.py migrate --database=items

# Clean up cache
echo "Cleaning up cache files..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Security check
echo "Running security checks..."
python manage.py check --deploy

# Verify static files
echo "Verifying static files..."
if [ -d "staticfiles" ]; then
    echo "Static files collected successfully"
else
    echo "Warning: staticfiles directory not found"
fi

# Compress static files
if command -v gzip &> /dev/null; then
    find staticfiles -type f -regextype posix-extended -regex ".*\.(css|js|txt|html|xml)" -exec gzip -f -k {} \;
fi

# Set proper permissions
chmod -R 755 staticfiles/

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

echo "Build completed successfully!"
