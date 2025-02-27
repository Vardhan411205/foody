#!/usr/bin/env bash
# This line tells the system to use the bash interpreter

# exit on error
set -o errexit
# This makes the script exit immediately if any command fails (returns non-zero)

cd /opt/render/project/src/

# Install Python dependencies
pip install -r requirements.txt
# Installs all Python packages listed in requirements.txt

# Collect static files
python manage.py collectstatic --no-input
# Gathers all static files (CSS, JS, images) into a single directory for production
# --no-input flag skips any prompts

# Run database migrations
python manage.py migrate
# Applies any pending database migrations to keep your database schema up to date 