from pydoc import plain
from celery import shared_task, group
from django.http import HttpResponse, JsonResponse

from product_tracker.models import Product
from .tables import ProductTableForEmail

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from users.models import User

from django.utils import timezone


@shared_task
def refresh_product(id):
    product = Product.objects.get(pk=id)
    if product.fetch_price():
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

def send_product_sale_email_for_user(user, products_on_sale, intro, send_even_if_nothing_on_sale):
    # user = User.objects.get(pk=userId)

    table = ProductTableForEmail(products_on_sale)
    num_products_on_sale = products_on_sale.count()

    context = {'products_table': table,
               'intro': intro,
               'name': user.first_name,
               'num_products_on_sale': num_products_on_sale}

    html_message = render_to_string('product_tracker/product_sale_email_template.html', context)

    def generatePlainTextMessage():
        msg = f"Hi {user.first_name},\n\n" if user.first_name else ""

        msg = msg + intro + "\n\n"

        for product in products_on_sale:
            msg = msg + f"{product.name} ({product.shop}) - Current price: ${product.current_price}, Savings: {product.savings_percentage}%\n"

            # indicate sale has been notified to the user
            product.sale_notified_to_user = True
            product.save()

        return msg

    plain_message = generatePlainTextMessage()

    if send_even_if_nothing_on_sale or num_products_on_sale > 0:
        mail.send_mail("Priceless Updates", plain_message, from_email="thepricelessapp@gmail.com", recipient_list=[user.email], html_message=html_message)


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