python3 manage.py makemigrations
python3 manage.py migrate
python manage.py loaddata ./fixturefiles/ImageMetadata.json
gunicorn --workers=4 --bind=127.0.0.1:8000 settings.wsgi:application --reload