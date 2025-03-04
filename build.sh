#!/bin/bash

# Create dummy tput command
echo '#!/bin/bash' > /tmp/tput
echo 'exit 0' >> /tmp/tput
chmod +x /tmp/tput
export PATH="/tmp:$PATH"

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn --no-cache-dir

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
