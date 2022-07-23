from django.urls import path, include
from .views import delete_product_view, products_view, add_product_view, update_product_view, products_refresh_all, update_product_url_view

urlpatterns = [
    path('products', products_view, name='products'),
    path('products/add', add_product_view, name='add-product'),
    path('product/update', update_product_view, name='update-product'),
    path('products/refreshall', products_refresh_all, name='refresh-all-products'),
    path('product/delete', delete_product_view, name='delete-product'),
    path('product/update-url', update_product_url_view, name='update-product-url'),
]
