from unittest.mock import patch
from django.test import TestCase
from .models import Product, WoolworthsProduct
from users.models import User
from unittest import skip

class WoolworthsProductTestCase(TestCase):
    def setUp(self):
        """Create a product and a user for testing"""
        self.user = User.objects.create(email="example@example.com", password="secret")
        product_full_cream_milk_url = 'https://www.woolworths.com.au/shop/productdetails/888137/woolworths-full-cream-milk'
        self.product_full_cream_milk = WoolworthsProduct.objects.create(url=product_full_cream_milk_url, user=self.user)

    def test_get_api_endpoint(self):
        """Tests correctly generating api endpoint url from product url"""
        expected_api_url = 'https://www.woolworths.com.au/apis/ui/product/detail/888137'
        actual_api_url = self.product_full_cream_milk.get_api_endpoint()
        self.assertEqual(actual_api_url, expected_api_url)

    @patch("product_tracker.models.WoolworthsProduct.fetch_data")
    def test_fetch_price_with_no_sale(self, mock_fetch_data):
        """Tests correctly parses and saves new price information from mock api data for product not on sale"""

        mock_fetch_data.return_value = {
            'Product': {
                'Price': 3.1,
                'Name': 'Woolworths Full Cream Milk',
                'WasPrice': 3.1,
                'SmallImageFile': 'https://cdn0.woolworths.media/content/wowproductimages/small/888137.jpg',
            }
        }
        self.product_full_cream_milk.fetch_price()  # fetch_price calls fetch_data
        self.assertEqual(self.product_full_cream_milk.current_price, 3.1)
        self.assertEqual(self.product_full_cream_milk.was_price, 3.1)
        self.assertEqual(self.product_full_cream_milk.name, 'Woolworths Full Cream Milk')
        self.assertEqual(self.product_full_cream_milk.on_sale, False)

    @patch("product_tracker.models.WoolworthsProduct.fetch_data")
    def test_fetch_price_with_sale(self, mock_fetch_data):
        """Tests correctly parses and saves new price information from mock api data for product on sale"""

        mock_fetch_data.return_value = {
            'Product': {
                'Price': 3.1,
                'Name': 'Woolworths Full Cream Milk',
                'WasPrice': 4.1,
                'SmallImageFile': 'https://cdn0.woolworths.media/content/wowproductimages/small/888137.jpg',
            }
        }
        self.product_full_cream_milk.fetch_price()  # fetch_price calls fetch_data
        self.assertEqual(self.product_full_cream_milk.current_price, 3.1)
        self.assertEqual(self.product_full_cream_milk.was_price, 4.1)
        self.assertEqual(self.product_full_cream_milk.name, 'Woolworths Full Cream Milk')
        self.assertEqual(self.product_full_cream_milk.on_sale, True)

    @skip
    def test_live_api_endpoint_response_success(self):
        """Tests product api endpoint response (through proxy) is successful"""
        api_url = self.product_full_cream_milk.get_api_endpoint()
        self.product_full_cream_milk.fetch_data(api_url)


