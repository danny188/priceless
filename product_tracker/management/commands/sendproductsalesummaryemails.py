from django.core.management.base import BaseCommand, CommandError
import requests
import json
import os

class Command(BaseCommand):
    help = 'Triggers the sending of all discount notification emails'

    def handle(self, *args, **options):
        url = 'http://localhost:8000/job/sendproductsalesummaryemails'
        data = {}
        headers = {'App-Password': os.environ.get("APP_PASSWORD", 'secret')}

        r = requests.post(url, data=json.dumps(data), headers=headers)