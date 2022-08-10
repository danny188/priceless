release: python3 manage.py migrate && python3 manage.py collectstatic --noinput
web: gunicorn priceless_project.wsgi
worker: celery -A priceless_project worker --pool=eventlet --concurrency=20 --loglevel=INFO