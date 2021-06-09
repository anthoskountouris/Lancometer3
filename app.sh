#!/bin/bash

ARGS="$ARGS --bind 0.0.0.0:8080 --workers 3"

exec gunicorn $ARGS wsgi:app
