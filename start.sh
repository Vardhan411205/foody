#!/bin/bash

# Disable color output
export TERM=dumb
export NO_COLOR=1

# Activate virtual environment
source venv/bin/activate

# Start gunicorn
exec venv/bin/gunicorn a.wsgi:application --bind 0.0.0.0:$PORT 