from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from product_tracker.models import WoolworthsProduct
from django.core.paginator import Paginator

@login_required
def products_view(request):
    # urls = ['https://www.woolworths.com.au/shop/productdetails/176564/d-orsogna-shortcut-bacon']

    # bacon = WoolworthsProduct(url=urls[0])
    # bacon.fetch_price()


    # bacon.save()

    # request.user.products.add(bacon)

    products = sorted(request.user.products.all().order_by('name'), key = lambda p: -p.savings_dollars())

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
        new_url = request.POST.get("new_url")
        new_woolworths_product = WoolworthsProduct(url=new_url)
        new_woolworths_product.fetch_price()
        new_woolworths_product.save()
        request.user.products.add(new_woolworths_product)
        return HttpResponseRedirect('/products')
