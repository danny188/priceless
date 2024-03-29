from django.urls import path, include
from .views import about_view, delete_product_view, get_progress_view, products_view, add_product_view, products_refresh_all, unsubscribe_confirm_view, unsubscribe_emails_view, update_product_url_view, job_update_all_products_view, job_send_product_sale_summary_emails_view, job_send_daily_product_sale_emails_view, refresh_single_product_view, email_preview_view


urlpatterns = [
    path('products', products_view, name='products-list'),
    path('products/add', add_product_view, name='add-product'),
    # path('product/update', update_product_view, name='update-product'),
    path('products/refreshallforuser', products_refresh_all, name='refresh-all-products-for-user'),
    path('product/<int:id>/refresh', refresh_single_product_view, name='refresh-single-product'),
    path('product/delete', delete_product_view, name='delete-product'),
    path('product/update-url', update_product_url_view, name='update-product-url'),
    path('products/refreshallforuser/get_progress', get_progress_view, name='progress-refresh-all-products-for-user'),
    path('job/updateallproducts', job_update_all_products_view, name='job-update-all-products'),
    path('job/sendproductsalesummaryemails', job_send_product_sale_summary_emails_view, name='job-send-product-sale-summary-emails'),
    path('job/senddailyproductsaleemails', job_send_daily_product_sale_emails_view, name='job-send-daily-product-sale-emails'),
    path('about', about_view, name='about'),
    path('', about_view, name='landing'),
    path('email_preview', email_preview_view, name='email-preview'),
    path('unsubscribe_confirm', unsubscribe_confirm_view, name='unsubscribe-confirm'),
    path('unsubscribe', unsubscribe_emails_view, name='unsubscribe-emails'),
]
