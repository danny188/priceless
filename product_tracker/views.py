import os
from dataclasses import field
from difflib import restore
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from product_tracker.models import WoolworthsProduct, Product
from django.core.paginator import Paginator
from django.contrib import messages

from product_tracker.tables import ProductTable
from .tasks import refresh_all_products, refresh_all_products_for_user, send_product_sale_summary_emails, send_daily_product_sale_emails
from django.views.decorators.csrf import csrf_exempt
import celery.result
import django_filters
from django import forms
from bs4 import BeautifulSoup

from users.models import User


@login_required
def products_view(request):
    # urls = ['https://www.woolworths.com.au/shop/productdetails/176564/d-orsogna-shortcut-bacon']

    # bacon = WoolworthsProduct(url=urls[0])
    # bacon.fetch_price()


    # bacon.save()

    # request.user.products.add(bacon)

    products = sorted(request.user.product_set.all().order_by('name'), key = lambda p: -p.calculate_savings_dollars())
    on_sale_products = request.user.product_set.filter(on_sale=True)

    # charcoal = products.get(pk=10)
    # charcoal.image_url = 'https://cdn0.woolworths.media/content/wowproductimages/small/176564.jpg'
    # charcoal.save()

    filter = ProductFilter(request.GET, queryset=request.user.product_set.all())

    # paginator = Paginator(filter.qs, 4)

    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    table = ProductTable(filter.qs)
    # print(table.as_html(request))
    context = {'products': products,
            #    'page_obj': page_obj,
               'on_sale_products': on_sale_products,
               'filter': filter,
               'product_table': table}

    return render(request, "product_tracker/products.html", context=context)


def add_product_view(request):
    if request.method == "POST":
        # todo check duplicate url
        # todo check valid url
        new_url = request.POST.get("new_url")

        # todo: instantiate product class by product shop type
        product = WoolworthsProduct.objects.create(url=new_url, user=request.user)
        product.fetch_price()
        product.save()

        messages.success(request, product.name + ' has been added.', extra_tags="is-success is-light")

    return render(request, "product_tracker/add_product.html")


# def update_product_view(request):
#     if request.method == "POST":
#         product_id = request.POST.get("product_pk")
#         product = WoolworthsProduct.objects.get(pk=product_id)
#         product.url = request.POST.get("updated_url")
#         product.fetch_price()
#         product.save()

#         return HttpResponseRedirect('/products')

@login_required
def products_refresh_all(request):
    if request.method == "POST":
        group_result_id = refresh_all_products_for_user(request.user)

        return JsonResponse({'group_result_id': group_result_id})


@login_required
def get_progress_view(request):
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
            'msg': 'product not found'
        })


@login_required
def update_product_url_view(request):

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        new_url = request.POST.get("updated_url")

        product = request.user.product_set.get(pk=product_id)

        if product:
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
            # return html
            # return HttpResponse(product_row_html)

            # return render(request, 'product_tracker/single_product.html', context=context)
            # return HttpResponseRedirect('/products')



def filter_on_sale(queryset, name, value):
    if value == 'both':
        return queryset
    elif value == 'on_sale':
        return queryset.filter(on_sale=True)
    else:
        return queryset.filter(on_sale=False)


class ProductFilter(django_filters.FilterSet):
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
    app_password = request.META.get('HTTP_APP_PASSWORD')

    if app_password == os.environ.get("APP_PASSWORD", 'secret'):
        group_result_id = refresh_all_products()

        return JsonResponse({'group_result_id': group_result_id})


@csrf_exempt
def job_send_product_sale_summary_emails_view(request):
    app_password = request.META.get('HTTP_APP_PASSWORD')

    if app_password == os.environ.get("APP_PASSWORD", 'secret'):
        group_result_id = send_product_sale_summary_emails()

        return JsonResponse({'group_result_id': group_result_id})

@csrf_exempt
def job_send_daily_product_sale_emails_view(request):
    app_password = request.META.get('HTTP_APP_PASSWORD')

    if app_password == os.environ.get("APP_PASSWORD", 'secret'):
        group_result_id = send_daily_product_sale_emails()

        return JsonResponse({'group_result_id': group_result_id})

