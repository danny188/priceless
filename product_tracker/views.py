from difflib import restore
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from product_tracker.models import WoolworthsProduct, Product
from django.core.paginator import Paginator
from django.contrib import messages
from .tasks import refresh_all_products_for_user
from django.views.decorators.csrf import csrf_exempt
import celery.result

@login_required
def products_view(request):
    # urls = ['https://www.woolworths.com.au/shop/productdetails/176564/d-orsogna-shortcut-bacon']

    # bacon = WoolworthsProduct(url=urls[0])
    # bacon.fetch_price()


    # bacon.save()

    # request.user.products.add(bacon)

    products = sorted(request.user.product_set.all().order_by('name'), key = lambda p: -p.savings_dollars())
    on_sale_products = request.user.product_set.filter(on_sale=True)

    # charcoal = products.get(pk=10)
    # charcoal.image_url = 'https://cdn0.woolworths.media/content/wowproductimages/small/176564.jpg'
    # charcoal.save()

    paginator = Paginator(products, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'products': products, 'page_obj': page_obj, 'on_sale_products': on_sale_products}

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
@csrf_exempt
def products_refresh_all(request):
    if request.method == "POST":
        group_result_id = refresh_all_products_for_user(request.user)

        return JsonResponse({'group_result_id': group_result_id})


@login_required
@csrf_exempt
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
        product = request.user.product_set.get(pk=product_id)

        if product:
            product.delete()

        return HttpResponseRedirect('/products')

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

            return render(request, 'product_tracker/single_product.html', context=context)
