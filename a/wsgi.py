"""
WSGI config for a project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a.settings')

# Get the WSGI application
application = get_wsgi_application()

# Development server configuration
if __name__ == "__main__":
    import sys
    from django.core.management import execute_from_command_line
    
    # Force the development server to use HTTP
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['wsgi.url_scheme'] = 'http'
    
    # Run the development server
    execute_from_command_line(sys.argv)
