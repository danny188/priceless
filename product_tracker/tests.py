from django.test import TestCase
from .models import Product

class ProductSortTestCase(TestCase):
    def setUp(self):
        Product.objects.create()

