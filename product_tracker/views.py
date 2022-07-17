from django.shortcuts import render

from product_tracker.models import WoolworthsProduct

def products_view(request):
    urls = ['https://www.woolworths.com.au/shop/productdetails/53385?region_id=201800&utm_source=google&utm_medium=cpc&utm_campaign=WW-0001&cq_net=u&cq_src=GOOGLE&cq_cmp=Woolies_8458_BAU_Shopping_Smart%20%26%20LIA_Beauty_WW-0001&cq_med=71700000085455714&cq_con=Smart%20Shopping%20Beauty&cq_plac=&cq_term=PRODUCT_GROUP&ds_adt=&cq_plt=gp&cq_gclid=CjwKCAjw5s6WBhA4EiwACGncZTm6UMJvmiIinu8tJUUSJ6ovsaaGhSC84CSrnILnzVC28b5_WkFX3RoC4fQQAvD_BwE&ds_de=c&ds_pc=online&ds_cr=586247646700&ds_tid=pla-1641195097378&ds_locphys=9071770&ds_pid=53385&cmpid=smsm:ds:GOOGLE:Woolies_8458_BAU_Shopping_Smart%20%26%20LIA_Beauty_WW-0001:PRODUCT_GROUP&gclid=CjwKCAjw5s6WBhA4EiwACGncZTm6UMJvmiIinu8tJUUSJ6ovsaaGhSC84CSrnILnzVC28b5_WkFX3RoC4fQQAvD_BwE&gclsrc=aw.ds']
    
    diffuser = WoolworthsProduct(urls[0])
    diffuser.fetch_price()
    
    context = {'product': diffuser}
    
    return render(request, "products.html", context=context)
