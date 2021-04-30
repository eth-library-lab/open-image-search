echo "wait 10s to allow DB to start"
sleep 10
python3 manage.py makemigrations ImageSearch # add each app here to ensure Django sees migrations
python3 manage.py migrate
python manage.py loaddata ./fixtures/ImageMetadata.json
gunicorn --bind=0.0.0.0:8000 --threads=2 --workers=4 settings.wsgi --reload
# have to bind to 0.0.0.0