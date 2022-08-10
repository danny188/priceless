python manage.py collectstatic --noinput
release: python3 manage.py migrate
web: gunicorn priceless_project.wsgi
worker: celery -A priceless_project worker --pool=eventlet --concurrency=20 --loglevel=INFO