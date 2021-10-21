#!/bin/bash

python3 manage.py makemigrations ImageSearch # add each app here to ensure Django sees migrations
python3 manage.py migrate ImageSearch
gunicorn --bind=0.0.0.0:$PORT --threads=8 --workers=1 settings.wsgi --reload
# have to bind to 0.0.0.0

