python3 manage.py makemigrations ImageSearch
python3 manage.py migrate
python manage.py loaddata ./fixtures/ImageMetadata.json
gunicorn --bind=0.0.0.0:8000 --threads=2 --workers=4 settings.wsgi --reload
# have to bind to 0.0.0.0