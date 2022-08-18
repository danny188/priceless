from celery import Celery
import os

# setting the Django settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'priceless_project.settings')
app = Celery()
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()