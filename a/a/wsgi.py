"""
WSGI config for a project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a.settings')

# Initialize WSGI application
application = get_wsgi_application()

# Add localhost configuration
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(["", "runserver", "localhost:8000"])
