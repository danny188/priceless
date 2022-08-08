from celery import shared_task, group
from django.http import HttpResponse, JsonResponse

from product_tracker.models import Product
from .tables import ProductTableForEmail

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from users.models import User


@shared_task
def refresh_product(id):
    product = Product.objects.get(pk=id)
    product.fetch_price()
    product.save()


@shared_task
def refresh_all_products():
    products = Product.objects.all()

    job = group([refresh_product.s(product.id) for product in products])

    result = job.apply_async(expires=120)

    result.save()

    return result.id

@shared_task
def refresh_all_products_for_user(user):
    """Activates background task to update all products for a user

    Args:
        user User: django user object

    Returns:
        str: group result id of the celery tasks
    """
    products = user.product_set.all()

    job = group([refresh_product.s(product.id) for product in products])

    result = job.apply_async(expires=120)
    result.save()

    return result.id

    # import time
    # while True:
    #     if result.ready():
    #         break
    #     time.sleep(0.5)
    #     print(str(result.completed_count()) + ' tasks out of ' + str(total_tasks) + ' completed.')


    # result.join()


@shared_task
def send_product_sale_summary_email_for_user(user):
    '''Sends a notification email to a user containing a list of products on sale'''
    # get list of products on sale
    products_on_sale = user.product_set.filter(on_sale=True)

    table = ProductTableForEmail(products_on_sale)

    context = {'products_table': table,
               'intro': "Here are your products that are currently on sale:",
               'name': user.first_name}

    html_message = render_to_string('product_tracker/product_sale_email_template.html', context)
    plain_message=strip_tags(html_message)
    mail.send_mail("Priceless Updates",plain_message, from_email="thepricelessapp@gmail.com", recipient_list=['dyhh12@gmail.com'], html_message=html_message)


@shared_task
def send_product_sale_summary_emails():
    '''Sends notification emails to all users containing a list of products on sale'''

    users = User.objects.all()

    job = group([send_product_sale_summary_email_for_user.s(user) for user in users])

    result = job.apply_async(expires=120)
    result.save()

    return result.id