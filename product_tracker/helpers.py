from .tables import ProductTableForEmail
from django.http import QueryDict, HttpResponse, JsonResponse
from django.urls import reverse
import os
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth.hashers import make_password

def format_time_delta(delta):
    """Generates a string representation of a time delta object

    Args:
        delta (timedelta): timedelta object

    Returns:
        string: formatted string to display time delta
    """
    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60 * SECONDS_IN_MINUTE

    seconds = delta.total_seconds()
    hours, remainder = divmod(delta.total_seconds(), MINUTES_IN_HOUR)
    minutes, seconds = divmod(remainder, SECONDS_IN_MINUTE)

    seconds, minutes, hours = round(seconds), round(minutes), round(hours)

    if hours:
        return f"{hours} hours, {minutes} minutes, {seconds} seconds"
    elif minutes:
        return f"{minutes} minutes, {seconds} seconds"
    elif seconds:
        return f"{seconds} seconds"
    else:
        return ""


def send_product_sale_email_for_user(user, products_on_sale, intro, send_even_if_nothing_on_sale):
    """Sends a product sale notification email for a user

    Args:
        user (User): user object
        products_on_sale (QuerySet): set of on-sale products
        intro (str): intro text in email
        send_even_if_nothing_on_sale (bool): whether to send the email anyway even if no products on sale
    """
    email = generate_product_sale_email_for_user(user, products_on_sale, intro)

    if send_even_if_nothing_on_sale or products_on_sale.count() > 0:
        mail.send_mail("Priceless Updates", email['plain_message'], from_email="thepricelessapp@gmail.com", recipient_list=[user.email], html_message=email['html_message'])


def generate_product_sale_email_for_user(user, products_on_sale, intro):
    """Generates a product sale summary email for a user

    Args:
        user (User): user object
        products_on_sale (QuerySet): set of on-sale products
        intro (str): intro text in email
        send_even_if_nothing_on_sale (bool): whether to send the email anyway even if no products on sale

    Returns:
        dict:
            key: html_message
            value (str): content of html email

            key: plain_email
            value (str): plain text version of email
    """
    # user = User.objects.get(pk=userId)

    table = ProductTableForEmail(products_on_sale)
    num_products_on_sale = products_on_sale.count()

    # generate link to unsubscribe from all emails
    unsubscribe_token = make_password(user.email + os.environ.get("APP_PASSWORD", 'secret'))
    unsubscribe_base_url = reverse('unsubscribe-confirm')
    params = QueryDict('', mutable=True)
    params.update({
        'email': user.email,
        'unsubscribe_token': unsubscribe_token
    })
    unsub_query_string = params.urlencode()

    unsubscribe_link = f"{unsubscribe_base_url}?{unsub_query_string}"

    context = {'products_table': table,
               'intro': intro,
               'name': user.first_name,
               'num_products_on_sale': num_products_on_sale,
               'unsubscribe_link': unsubscribe_link}

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

    return {'html_message' : html_message, 'plain_message': plain_message}

