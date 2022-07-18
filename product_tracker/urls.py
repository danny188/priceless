from django.urls import path, include
from .views import products_view, add_product_view, update_product_view

urlpatterns = [
    path('products', products_view, name='products'),
    path('products/add', add_product_view, name='add-product'),
    path('product/update', update_product_view, name='update-product'),

]
