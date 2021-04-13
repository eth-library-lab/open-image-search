# Django API 


## Start Up

    backend/api$ python3 manage.py makemigrations
    backend/api$ python3 manage.py migrate
    backend/api$ python manage.py loaddata ../../search-model/data/processed/fixtures/ImageMetadata.json
    backend/api$ python manage.py runserver

## Deployment

make new secret key

    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())
