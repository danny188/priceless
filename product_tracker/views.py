import os
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from product_tracker.exceptions import ProductURLError
from product_tracker.helpers import format_time_delta
from product_tracker.models import Product
from django.contrib import messages

from django.contrib.auth.hashers import check_password

from product_tracker.tables import ProductTable
from .tasks import refresh_all_products, refresh_all_products_for_user, send_product_sale_summary_emails, send_daily_product_sale_emails
from django.views.decorators.csrf import csrf_exempt
import celery.result
import django_filters
from django import forms
from bs4 import BeautifulSoup

from users.models import User

from urllib.parse import urlparse
from django.utils import timezone
from datetime import timedelta

from .helpers import generate_product_sale_email_for_user

import logging

logger = logging.getLogger(__name__)


@login_required
def products_view(request):
    """Displays a list of user's products

    Returns:
        HttpResponse: page to display user's products
    """
    products = sorted(request.user.product_set.all().order_by('name'), key = lambda p: -p.calculate_savings_dollars())
    on_sale_products = request.user.product_set.filter(on_sale=True)

    filter = ProductFilter(request.GET, queryset=request.user.product_set.all())

    table = ProductTable(filter.qs)

    context = {'products': products,
               'on_sale_products': on_sale_products,
               'filter': filter,
               'product_table': table}

    return render(request, "product_tracker/products.html", context=context)


def add_product_view(request):
    """Add a product to a user's collection

    Returns:
        HttpResponse: page to add a product
    """

    # pass in current list of supported shops
    context = {'supported_shops': ','.join(Product.get_supported_shops()),}

    if request.method == "POST":
        new_url = request.POST.get("new_url").strip()

        try:
            # check valid url
            Product.validate_url(new_url, request.user)

            # validate beofre save
            url_obj = urlparse(new_url)
            hostname = url_obj.hostname.replace('www.', '')

            product_model = Product.get_product_model(hostname)

            # instantiate product class by product shop type
            product = product_model.objects.create(url=new_url, user=request.user)

            product.fetch_price()
            product.save()

            messages.success(request, product.name + ' has been added.', extra_tags="is-success is-light")
        except ProductURLError as url_error:
            product.delete()
            messages.error(request, f"Product could not be added: {url_error.message}", extra_tags="is-danger is-light")

    return render(request, "product_tracker/add_product.html", context)


@login_required
def refresh_single_product_view(request, id):
    """Refresh a single product

    Args:
        request (_type_): _description_
        id (_type_): _description_

    Returns:
        JsonResponse: result of operation, and product counts if successful
    """
    if request.method == "POST":
        product = request.user.product_set.get(pk=id)

        if product:
            # only refresh product if max refresh frequency not exceeded
            now = timezone.now()
            time_diff = now - product.last_price_check
            next_refresh_time_permitted = product.last_price_check + timedelta(minutes=Product.MAX_REFRESH_FREQUENCY)
            waiting_time = next_refresh_time_permitted - now
            if (time_diff) < timedelta(minutes=Product.MAX_REFRESH_FREQUENCY):
                return JsonResponse({
                    'result': 'info',
                    'msg': 'A product refresh is limited to every ' + str(Product.MAX_REFRESH_FREQUENCY) + ' minutes. Please try again in ' + format_time_delta(waiting_time)})

            try:
                product.fetch_price()
                product.save()

                # generate table
                filter = ProductFilter(request.GET, queryset=request.user.product_set.all())
                table = ProductTable(filter.qs)

                num_products_on_sale = filter.qs.filter(on_sale=True).count()

                # get html of table
                table_html = table.as_html(request)

                # use bs to get html of row for product
                soup = BeautifulSoup(table_html, 'html.parser')

                row_tds = soup.select('#row-for-product-' + str(product.id) + ' td')

                row_tds_inner_html = map(lambda td: td.decode_contents().strip(), row_tds)

                return JsonResponse({
                    'result': 'success',
                    'row_data': list(row_tds_inner_html),
                    'num_products_on_sale': num_products_on_sale,})
            except ProductURLError as url_error:
                return JsonResponse({
                    'result': 'error',
                    'error_msg': url_error.message,})
        else:
            return JsonResponse({
                    'result': 'error',
                    'error_msg': 'Product not found'})


@login_required
def products_refresh_all(request):
    """Refresh all products in the database

    Returns:
        JsonResponse:
            group_result_id: celery group id for monitoring tasks list
    """
    if request.method == "POST":
        group_result_id = refresh_all_products_for_user(request.user)

        return JsonResponse({'group_result_id': group_result_id})


@login_required
def get_progress_view(request):
    """Returns the number of completed and total tasks given a Celery group_result_id

    Args:
        request object query parameter:
            group_result_id - Celery group_result_id

    Returns:
        JsonResponse:
            total - total number of tasks
            completed_count - number of completed tasks
    """
    if request.method == "GET":
        group_set_id = request.GET.get('group_result_id')
        restored_group_result = celery.result.GroupResult.restore(group_set_id)
        completed_count = restored_group_result.completed_count()
        total = len(restored_group_result.children)

        if completed_count >= total:
            restored_group_result.forget()

        return JsonResponse({'total': total, 'completed_count': completed_count})


@login_required
def delete_product_view(request):
    """Deletes a single product

    Args:
        request (_type_): _description_

    Returns:
        json: result of operation, product number counts
    """
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        qs = request.user.product_set
        product = qs.get(pk=product_id)


        if product:
            product.delete()
            num_products = qs.count()
            num_products_on_sale = qs.filter(on_sale=True).count()

            return JsonResponse({
                'result': 'success',
                'num_products': num_products,
                'num_products_on_sale': num_products_on_sale,
            })

        return JsonResponse({
            'result': 'error',
            'error_msg': 'product not found'
        })


@login_required
def update_product_url_view(request):
    """Updates the url of a product

    Args:
        request object query parameter:
            product_id - id of product
            updated_url - new url of product

    Returns:
        JsonResponse: _description
    """
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        new_url = request.POST.get("updated_url")

        product = request.user.product_set.get(pk=product_id)

        if product:
            try:
                product.url = new_url
                product.fetch_price()
                product.save()
                context = {'product': product}

                # generate table
                filter = ProductFilter(request.GET, queryset=request.user.product_set.all())
                table = ProductTable(filter.qs)

                num_products_on_sale = filter.qs.filter(on_sale=True).count()

                # get html of table
                table_html = table.as_html(request)

                # use bs to get html of row for product
                soup = BeautifulSoup(table_html, 'html.parser')
                product_row_html = soup.select_one('#row-for-product-' + str(product.id))

                row_tds = soup.select('#row-for-product-' + str(product.id) + ' td')

                row_tds_inner_html = map(lambda td: td.decode_contents().strip(), row_tds)


                return JsonResponse({
                    'row_data': list(row_tds_inner_html),
                    'num_products_on_sale': num_products_on_sale,})
            except ProductURLError as url_error:
                return JsonResponse({
                    'result': 'error',
                    'error_msg': url_error.message,})
        else:
            return JsonResponse({
            'result': 'error',
            'msg': 'product not found'})


def filter_on_sale(queryset, name, value):
    """Returns a set of records filtered by products on sale, products not on sale, or all products.

    Args:
        queryset (QuerySet): original queryset
        name (_type_): name of the model field to filter on
        value (_type_): value to filter with

    Returns:
        QuerySet : filtered records
    """
    if value == 'both':
        return queryset
    elif value == 'on_sale':
        return queryset.filter(on_sale=True)
    else:
        return queryset.filter(on_sale=False)


class ProductFilter(django_filters.FilterSet):
    """Filter for products"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    current_price__gt = django_filters.NumberFilter(field_name='current_price', lookup_expr='gt')
    current_price__lt = django_filters.NumberFilter(field_name='current_price', lookup_expr='lt')
    savings_percentage__gt = django_filters.NumberFilter(field_name='savings_percentage', lookup_expr='gt')
    savings_percentage__lt = django_filters.NumberFilter(field_name='savings_percentage', lookup_expr='lt')
    savings_dollars__gt = django_filters.NumberFilter(field_name='savings_dollars', lookup_expr='gt')
    savings_dollars__lt = django_filters.NumberFilter(field_name='savings_dollars', lookup_expr='lt')
    # on_sale = django_filters.BooleanFilter(widget=forms.CheckboxInput)

    SHOP_CHOICES = (('Woolworths', 'Woolworths'), )

    shop = django_filters.MultipleChoiceFilter(choices=SHOP_CHOICES, field_name='shop', widget=forms.CheckboxSelectMultiple)

    ON_SALE_CHOICES = (('both', 'On-sale or standard-price'),
                       ('on_sale', 'On Sale'),
                       ('standard_price', 'Standard Price'),)
    on_sale = django_filters.ChoiceFilter(choices=ON_SALE_CHOICES, method=filter_on_sale)


    class Meta:
        model = Product
        fields = ['name']


@csrf_exempt
def job_update_all_products_view(request):
    """Update all products in the database. Designed to be called by a custom django admin command.

    Returns:
        JsonResponse: Celery group result id for tracking tasks
    """
    app_password = request.META.get('HTTP_APP_PASSWORD')

    if app_password == os.environ.get("APP_PASSWORD", 'secret'):
        logger.info("scheduled job activated: update all products in db")
        group_result_id = refresh_all_products()

        return JsonResponse({'group_result_id': group_result_id})
    else:
        logger.error("scheduled job (update all products in db): wrong app password used")


@csrf_exempt
def job_send_product_sale_summary_emails_view(request):
    """Sends product sale summary emails to all users. Designed to be called by a custom django admin command.

    Returns:
        JsonResponse: Celery group result id for tracking tasks
    """
    app_password = request.META.get('HTTP_APP_PASSWORD')

    if app_password == os.environ.get("APP_PASSWORD", 'secret'):
        logger.info("scheduled job activated: send product sale summary emails")
        group_result_id = send_product_sale_summary_emails()

        return JsonResponse({'group_result_id': group_result_id})
    else:
        logger.error("scheduled job (send product sale summary emails): wrong app password used")


@csrf_exempt
def job_send_daily_product_sale_emails_view(request):
    """Sends daily product sale emails to all users. Designed to be called by a custom django admin command.

    Returns:
        JsonResponse: Celery group result id for tracking tasks
    """
    app_password = request.META.get('HTTP_APP_PASSWORD')

    if app_password == os.environ.get("APP_PASSWORD", 'secret'):
        logger.info("scheduled job activated: send daily product sale emails")
        group_result_id = send_daily_product_sale_emails()

        return JsonResponse({'group_result_id': group_result_id})
    else:
        logger.error("scheduled job (send daily product sale emails): wrong app password used")


def about_view(request):
    """Show landing page of Priceless App"""
    return render(request, "product_tracker/about.html")


def email_preview_view(request):
    """For development use: previews product sale email for current user"""
    # from .tables import ProductTableForEmail
    user = request.user
    products_on_sale = user.product_set.filter(on_sale=True)
    intro = "Here are the products currently on sale:"

    # table = ProductTableForEmail(products_on_sale)
    # num_products_on_sale = products_on_sale.count()
    # context = {'products_table': table,
    #            'intro': "Here are the products currently on sale:",
    #            'name': user.first_name,
    #            'num_products_on_sale': num_products_on_sale}

    email = generate_product_sale_email_for_user(user, products_on_sale, intro)
    html_email = email['html_message']

    return HttpResponse(html_email)
    return render(request, "product_tracker/product_sale_email_template.html", context)


def unsubscribe_confirm_view(request):
    """Returns the page to confirmi unsubscribe from emails"""
    context = {
        'unsubscribe_email': request.GET.get('email'),
        'unsubscribe_token': request.GET.get('unsubscribe_token'),
    }
    return render(request, "product_tracker/unsubscribe_confirm.html", context)


def unsubscribe_emails_view(request):
    """Unsubscribes a user from all emails"""

    unsubscribe_token = request.POST.get('unsubscribe-token')
    unsubscribe_email = request.POST.get('unsubscribe-email')

    if request.method == "POST":
        if (check_password(unsubscribe_email + os.environ.get('APP_PASSWORD', 'secret'), unsubscribe_token)):
            # todo: unsub all email for user
            user = User.objects.get(email=unsubscribe_email)
            user.receive_email_as_products_go_on_sale = False
            user.unsubscribe_all()
            user.save()
            return render(request, "product_tracker/unsubscribe_done.html")
        else:
            context = {
                'unsubscribe_email': unsubscribe_email,
                'unsubscribe_token': unsubscribe_token,
            }

            messages.warning(request, "Invalid unsubscribe token supplied", extra_tags="is-warning is-light")
            return render(request, "product_tracker/unsubscribe_confirm.html", context)

