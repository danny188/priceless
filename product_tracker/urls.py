from django.urls import path, include
from .views import products_view

urlpatterns = [
    path('products', products_view, name='products'),
]
