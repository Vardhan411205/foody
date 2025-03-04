#!/bin/bash

# Disable color output
export TERM=dumb
export NO_COLOR=1

# Start gunicorn
exec gunicorn a.wsgi:application --bind 0.0.0.0:$PORT 