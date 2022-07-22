from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from product_tracker.models import WoolworthsProduct, Product
from django.core.paginator import Paginator
from django.contrib import messages

@login_required
def products_view(request):
    # urls = ['https://www.woolworths.com.au/shop/productdetails/176564/d-orsogna-shortcut-bacon']

    # bacon = WoolworthsProduct(url=urls[0])
    # bacon.fetch_price()


    # bacon.save()

    # request.user.products.add(bacon)

    products = sorted(request.user.product_set.all().order_by('name'), key = lambda p: -p.savings_dollars())

    # charcoal = products.get(pk=10)
    # charcoal.image_url = 'https://cdn0.woolworths.media/content/wowproductimages/small/176564.jpg'
    # charcoal.save()

    paginator = Paginator(products, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'products': products, 'page_obj': page_obj}

    return render(request, "product_tracker/products.html", context=context)


def add_product_view(request):
    if request.method == "POST":
        # todo check duplicate url
        new_url = request.POST.get("new_url")
        # new_woolworths_product = WoolworthsProduct(url=new_url)

        product = WoolworthsProduct.objects.create(url=new_url, user=request.user)
        product.fetch_price()
        product.save()

        messages.success(request, product.name + ' has been added.', extra_tags="is-success is-light")
        # return HttpResponseRedirect('/products')
        return render(request, "product_tracker/add_product.html")
    else:
        return render(request, "product_tracker/add_product.html")

def update_product_view(request):
    if request.method == "POST":
        product_id = request.POST.get("product_pk")
        product = WoolworthsProduct.objects.get(pk=product_id)
        product.url = request.POST.get("updated_url")
        product.fetch_price()
        product.save()

        return HttpResponseRedirect('/products')
