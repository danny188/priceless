from pydoc import plain
from celery import shared_task, group

from product_tracker.exceptions import ProductURLError
from .helpers import send_product_sale_email_for_user

from product_tracker.models import Product

from users.models import User

from django.utils import timezone
import redis
import os
import datetime
import time


@shared_task
def refresh_product(id):
    """Refresh a single product

    Args:
        id (int): product id
    """
    product = Product.objects.get(pk=id)

    try:
        if product.fetch_price():
            product.save()
    except ProductURLError:
        pass


@shared_task
def dummy_refresh_product(id):
    """For debugging redis error of exceeding max number of client connections"""
    def get_redis():
        url = os.environ.get("REDIS_URL")

        if url:
            r = redis.from_url(url)  # use secure for heroku
        else:
            r = redis.Redis()  # use unauthed connection locally

        return r

    c = get_redis().info()['connected_clients']
    now = datetime.datetime.now()

    print("{} | Active redis connections: {}".format(now, c))

    try:
        time.sleep(6)
    except ProductURLError:
        pass


@shared_task
def refresh_all_products():
    """Refresh all products in entire database

    Returns:
        str: Celery group result id for monitoring task state
    """
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




@shared_task
def send_daily_product_sale_email_for_user(userId):
    '''Sends a daily notification email to user informing of new sales (no email is sent if nothing on sale)'''

    user = User.objects.get(pk=userId)
    products_on_sale = user.product_set.filter(on_sale=True).filter(sale_notified_to_user=False)
    send_product_sale_email_for_user(user, products_on_sale,'Here are the products that newly went on sale:', False)


@shared_task
def send_product_sale_summary_email_for_user(userId):
    '''Sends a weekly notification email to a user containing a list of products on sale'''

    user = User.objects.get(pk=userId)
    products_on_sale = user.product_set.filter(on_sale=True)
    send_product_sale_email_for_user(user, products_on_sale, 'Here are your products that are currently on sale:', True)


@shared_task
def send_product_sale_summary_emails():
    '''Sends notification emails to all users containing a list of products on sale'''

    current_iso_week_day = timezone.now().isoweekday()
    users = User.objects.filter(receive_product_sale_summary_email=True).filter(summary_email_day_of_week=current_iso_week_day)

    job = group([send_product_sale_summary_email_for_user.s(user.id) for user in users])

    result = job.apply_async(expires=120)
    result.save()

    return result.id


@shared_task
def send_daily_product_sale_emails():
    '''Sends notification emails to all users containing a list of products on sale
        that weren't previously notified to the user'''

    users = User.objects.filter(receive_email_as_products_go_on_sale=True)

    job = group([send_daily_product_sale_email_for_user.s(user.id) for user in users])

    result = job.apply_async(expires=120)
    result.save()

    return result.id