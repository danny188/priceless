release: python3 manage.py migrate
web: gunicorn priceless_project.wsgi
worker: celery -A pricess_project worker --pool=eventlet --concurrency=20 --loglevel=INFO