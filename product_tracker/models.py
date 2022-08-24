from distutils.log import error
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import models
from product_tracker.exceptions import ProductURLError
from users.models import User

import requests
from django.utils import timezone
import json

import re
from urllib.parse import urlparse

import environ
env = environ.Env(DEBUG=(bool, False))
# reading .env file
environ.Env.read_env()

import logging
logger = logging.getLogger(__name__)

class Product(models.Model):
    """Represents a product

    Raises:
        ProductURLError: any errors related to a product's url or api endpoint
    """
    MAX_REFRESH_FREQUENCY = 5  # limit to every 5 minutes at most

    on_sale = models.BooleanField(default=False)
    sale_notified_to_user = models.BooleanField(default=False)
    url = models.URLField(max_length=2000)
    image_url = models.URLField(max_length=2000, null=True)
    name = models.CharField(max_length=200)
    last_price_check = models.DateTimeField(null=True)
    current_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    was_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    product_type_by_shop = models.CharField(max_length=300)

    SHOP_CHOICES = (('Woolworths', 'Woolworths'),)

    shop = models.CharField(max_length=200, choices=SHOP_CHOICES)
    savings_percentage = models.IntegerField(blank=True, null=True)
    savings_dollars = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    @classmethod
    def get_hostname(cls, url):
        """Returns the hostname from a url"""
        return urlparse(url).hostname.replace('www.', '')


    @classmethod
    def get_product_model(cls, hostname):
        """Returns the class name of a particular shop's product

        Args:
            hostname (str): hostname of a product's shop

        Returns:
            type: class of a particular shop's product
        """
        if hostname == 'woolworths.com.au':
            return WoolworthsProduct


    @classmethod
    def get_supported_shops(cls):
        """Returns a list of currently supported shops

        Returns:
            list of str: supported shop names
        """
        return list(map(lambda x: x[0], cls.SHOP_CHOICES))

    @classmethod
    def validate_url(cls, url, user):
        """Checks if a product url is valid"""
        # checks url looks like an url
        try:
            url_validator = URLValidator()
            url_validator(url)
        except ValidationError:
            raise ProductURLError("Invalid URL")

        # check shop url is one of the supported shops
        url_hostname = cls.get_hostname(url)
        # if product model not found, it indicates that the shop of current url is not supported
        if not cls.get_product_model(url_hostname):
            supported_shops = cls.get_supported_shops()
            raise ProductURLError('URL hostname not currently supported. Currently supported shops include: ' + ','.join(supported_shops))

        # check url doens't already exist for user
        if user.product_set.filter(url=url):
            raise ProductURLError('An identical product URL already exists')



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # cast to proxy model instance
        if self.__class__ == Product:
            for _class in Product.__subclasses__():
                if self.product_type_by_shop == _class.__name__:
                    self.__class__ = _class
                    break


    def calculate_savings_dollars(self):
        """Returns the savings amount in dollars rounded to 2 decimal places"""
        if self.was_price and self.current_price:
            return round(abs(self.was_price - self.current_price), 2)
        else:
            return 0

    def calculate_savings_percentage(self):
        """Returns the savings as a percentage rounded to nearest integer"""
        if self.was_price and self.current_price:
            return round(self.calculate_savings_dollars() / self.was_price * 100)
        else:
            return 0

    user = models.ForeignKey(User, on_delete=models.CASCADE)


class WoolworthsProduct(Product):
    """Represents a product from Woolworths"""

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

    SHOP_FAVICON_URL = "https://cdn0.woolworths.media/wowssr/syd1/a10/browser/assets/images/favicon.ico?hash=0.0"
    SHOP_BASE_URL = "https://www.woolworths.com.au/"

    @classmethod
    def fetch_data(cls, url):
        """Requests product data from an api endpoint

        Args:
            url (str): api endpoint for product data

        Raises:
            ProductURLError: errors related to api endpoint responses

        Returns:
            json: product data
        """

        proxies = {
            'https': env('MY_HTTPS_PROXY'),
        }
        logger.info('request sent to url endpoint: ' + url)

        # debug: for enabling logs of requests module
        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

        response = requests.get(url, cookies=cls.COOKIES, headers=cls.HEADERS, proxies=proxies, verify=False)
        logger.info('response from url endpoint received')
        logger.info("response status code is " + str(response.status_code))
        logger.debug("response text is " + str(response.text))

        if response.status_code != 200:
            logger.error(f"error response from product url endpoint - status_code = {response.status_code}.")
            logger.error("response text is " + response.text)
            raise ProductURLError('Product data could not be retrieved')
        else:
            try:
                json_obj = response.json()
                return json_obj
            except:
                logger.error('Response from product api endpoint is not json')
                raise ProductURLError('Product data could not be retrieved')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_type_by_shop = self.__class__.__name__
        self.shop = 'Woolworths'


    def get_shop_favicon_url(self):
        return self.__class__.SHOP_FAVICON_URL


    def get_shop_base_url(self):
        return self.__class__.SHOP_BASE_URL


    def get_api_endpoint(self):
        """Returns the woolworths api endpoint from a product url"""

        def get_stock_code(url):
            """Extracts the stock code from a product url"""
            pattern = r"woolworths.com.au/shop/productdetails/(\d*)?"
            match = re.search(pattern, url)
            if match:
                stock_code = match.group(1)
                return stock_code
            else:
                logger.error('Error parsing URL for product stock code. Product URL was ' + url)
                raise ProductURLError(f'Error obtaining product stock code. Please check that you have entered a valid URL for a {self.shop} product')

        stock_code = get_stock_code(self.url)
        return f"https://www.woolworths.com.au/apis/ui/product/detail/{stock_code}"


    def parse_data(self, json_obj):
        """Extracts product data and saves to the product object"""
        self.current_price = json_obj['Product']['Price']
        self.name = json_obj['Product']['Name']
        self.was_price = json_obj['Product']['WasPrice']
        self.image_url = json_obj['Product']['SmallImageFile']
        self.last_price_check = timezone.now()
        self.savings_dollars = self.calculate_savings_dollars()
        self.savings_percentage = self.calculate_savings_percentage()

        if self.current_price != self.was_price and self.was_price:
            self.on_sale = True
        else:
            if self.on_sale:
                # if previously on sale, reset flag so user is notified of next sale
                self.sale_notified_to_user = False

            self.on_sale = False


    def fetch_price(self):
        """Updates the product's price from the saved url"""
        api_endpoint = self.get_api_endpoint()
        json_obj = self.__class__.fetch_data(api_endpoint)

        if json_obj and json_obj['Product']:  # check if product exists
            self.parse_data(json_obj)
            return True
        else:
            logger.error(f"Product fetch_price failed. Invalid data in json.")
            logger.error('json data: ' + str(json_obj))
            raise ProductURLError('Product data obtained was invalid')






