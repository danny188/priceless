from celery import shared_task, group

from product_tracker.models import Product

@shared_task
def adding_task(x, y):
    print('doing adding task')
    return x + y


@shared_task
def refresh_product(id):
    product = Product.objects.get(pk=id)
    product.fetch_price()
    product.save()
    print('finished updating product ' + str(product.id))


@shared_task
def refresh_all_products():
    products = Product.objects.all()

    job = group([refresh_product.s(product.id) for product in products])

    result = job.apply_async(expires=120)

    result.join()

@shared_task
def refresh_all_products_for_user(user):
    products = user.product_set.all()

    job = group([refresh_product.s(product.id) for product in products])

    result = job.apply_async(expires=120)

    result.join()