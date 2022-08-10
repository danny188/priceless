from distutils.log import error
from django.db import models
from users.models import User

import requests
from django.utils import timezone

import re
import os

import logging
logger = logging.getLogger(__name__)

class Product(models.Model):
    on_sale = models.BooleanField(default=False)
    sale_notified_to_user = models.BooleanField(default=False)
    url = models.URLField(max_length=2000)
    image_url = models.URLField(max_length=2000, null=True)
    name = models.CharField(max_length=200)
    last_price_check = models.DateTimeField(null=True)
    current_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    was_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    product_type_by_shop = models.CharField(max_length=200)

    SHOP_CHOICES = (('Woolworths', 'Woolworths'),)

    shop = models.CharField(max_length=200, choices=SHOP_CHOICES)
    savings_percentage = models.IntegerField(blank=True, null=True)
    savings_dollars = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # cast to proxy model instance
        if self.__class__ == Product:
            for _class in Product.__subclasses__():
                if self.product_type_by_shop == _class.__name__:
                    self.__class__ = _class
                    break

    def calculate_savings_dollars(self):
        if self.was_price and self.current_price:
            return round(abs(self.was_price - self.current_price), 2)
        else:
            return 0

    def calculate_savings_percentage(self):
        if self.was_price and self.current_price:
            return round(self.calculate_savings_dollars() / self.was_price * 100)
        else:
            return 0

    user = models.ForeignKey(User, on_delete=models.CASCADE)

class WoolworthsProduct(Product):
    class Meta:
        proxy = True

    COOKIES = {
        '_abck': '4634E7C8D7A92DF2C6DD2260DD955FE8~-1~YAAQxAfSF/2entuBAQAAEvxD5wiTsoSk7JoMnlM+Uz9z55+LrQ6YaOmueDWsnqm7h6ZqomqGH0JmkMJaayVV5C7iISg6Q575JBC/Nyrzv9l/F05UMxG7bzfyK0exU2czcpwDQKAN5A1z9rvX+ea6kZUEYbqJReBWKyINj8UxX40+Mif/Dy/XQDbwrFu107J3WvpgdkWV9G1XPlxoUH8bWK+cK1f9iskSITO5dLawxU5YGClTpyT7ZvOvfm5njjh0yQqWhCL48rkXyjQwr+ro+soje++zNG5eMOfvrLvRoRO7UyFZLoRNtqLcyj0ZY9iW4gOOHA9W7t8VC8SHJH6HYzzX/ZX29wGrV8tAPFfwU4OcpbSiJ19ulSPM8+b/DmBmFSx60VJm//Z6ldQsbNGkHh91g+h4Ay2YqsXadl5jTGE=~-1~-1~-1',
        'bm_sv': '3E4A343C9D852B2717DAF1C9CC343741~YAAQxAfSF/6entuBAQAAEvxD5xDQETa1skWg0jQ5qo1HER6nt/NQ+2yjWDta+OKMpcsLbEvgT29WX/ai8mo/GM+RPl7Q0Fbsrmx6dGR47QfJhTuMzHucCleIGZKWJbefCy6qaUQwpaGk/tlMoyoE6+uH3KgExTPd30JHm7BOywh0FAQhvx7KOBhCu53OjjH/DET7t7UTS1YNdz3AqAdRIKbaZk7p43KLvAjniU1sJWXNsJMpioVZ6h2hoZdZb5Ui5aCmgGzF0nA=~1',
    }

    HEADERS = {
        'authority': 'www.woolworths.com.au',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }


    @classmethod
    def fetch_data(cls, url):
        proxies = {
            'https': os.environ.get('HTTPS_PROXY'),
        }
        logger.info('request sent to url endpoint: ' + url)

        # for enabling logs of requests module
        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

        response = requests.get(url, cookies=cls.COOKIES, headers=cls.HEADERS, proxies=proxies, verify=False)
        logger.info('response from url endpoint received')
        logger.info("response status code is " + str(response.status_code))

        if response.status_code != 200:
            logger.error(f"error response from product url endpoint - status_code = {response.status_code}.")
            logger.error("response text is " + response.text)

        logger.debug("response text is " + str(response.text))

        json = response.json()
        return json

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_type_by_shop = self.__class__.__name__
        self.shop = 'Woolworths'

    def get_api_endpoint(self):
        def get_stock_code(url):
            pattern = r"productdetails/(\d*)?"
            match = re.search(pattern, url)
            if match:
                stock_code = match.group(1)
            else:
                stock_code = None

            return stock_code

        stock_code = get_stock_code(self.url)
        return f"https://www.woolworths.com.au/apis/ui/product/detail/{stock_code}"


    def parse_data(self, json):
        self.current_price = json['Product']['Price']
        self.name = json['Product']['Name']
        self.was_price = json['Product']['WasPrice']
        self.image_url = json['Product']['SmallImageFile']
        self.last_price_check = timezone.now()
        self.savings_dollars = self.calculate_savings_dollars()
        self.savings_percentage = self.calculate_savings_percentage()

        if self.current_price != self.was_price and self.was_price:
            self.on_sale = True
        else:
            self.on_sale = False

    def fetch_price(self):
        api_endpoint = self.get_api_endpoint()
        json = WoolworthsProduct.fetch_data(api_endpoint)
        self.parse_data(json)





