from django.urls import path, include
from .views import delete_product_view, get_progress_view, products_view, add_product_view, products_refresh_all, update_product_url_view

urlpatterns = [
    path('products', products_view, name='products'),
    path('products/add', add_product_view, name='add-product'),
    # path('product/update', update_product_view, name='update-product'),
    path('products/refreshallforuser', products_refresh_all, name='refresh-all-products-for-user'),
    path('product/delete', delete_product_view, name='delete-product'),
    path('product/update-url', update_product_url_view, name='update-product-url'),
    path('products/refreshallforuser/get_progress', get_progress_view, name='progress-refresh-all-products-for-user'),
]
