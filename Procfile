release: python manage.py migrate
web: gunicorn priceless_project.wsgi
worker: celery -A priceless_project worker --pool=eventlet --concurrency=5 --loglevel=INFO