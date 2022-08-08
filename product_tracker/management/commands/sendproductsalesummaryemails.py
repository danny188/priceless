from django.core.management.base import BaseCommand, CommandError
import requests
import json
import os
from django.urls import reverse

class Command(BaseCommand):
    help = 'Triggers the sending of all discount notification emails'

    def handle(self, *args, **options):
        url = os.environ.get('BASE_URL', 'http://localhost:8000') + reverse('job-send-product-sale-summary-emails')
        data = {}
        headers = {'App-Password': os.environ.get("APP_PASSWORD", 'secret')}

        r = requests.post(url, data=json.dumps(data), headers=headers)