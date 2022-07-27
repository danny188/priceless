from celery import shared_task, group
from django.http import HttpResponse, JsonResponse

from product_tracker.models import Product

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

    result.join()

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