web: gunicorn priceless_project.wsgi
worker: celery -A priceless_project worker --pool=eventlet --concurrency=20 --loglevel=INFO