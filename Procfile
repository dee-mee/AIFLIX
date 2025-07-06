web: poetry run python manage.py migrate && poetry run gunicorn aiflix.wsgi:application --log-file - --bind 0.0.0.0:$PORT --workers 3 --timeout 120
