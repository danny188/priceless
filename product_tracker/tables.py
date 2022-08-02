import django_tables2 as tables
from .models import Product

class ProductTable(tables.Table):
    image = tables.TemplateColumn("""
    {% if record.image_url %}
    <a href="{{record.url}}">
    <img class="product-thumbnail" src={{ record.image_url }}>
    </a>
    {% endif %}
    """, verbose_name='')

    sale_status = tables.TemplateColumn("""
    {% if record.on_sale %}
    <span class="tag is-warning">on sale</span></strong>
    {% endif %}
    """)

    price = tables.TemplateColumn("${{ record.current_price }}")
    was_price = tables.TemplateColumn("${{ record.was_price }}", verbose_name="Old Price")
    savings_percentage = tables.TemplateColumn("{{ record.savings_percentage }}%", verbose_name="Savings %")
    savings_dollars = tables.TemplateColumn("${{ record.savings_dollars }}", verbose_name="Savings $")

    name = tables.TemplateColumn("""
    {% if record.savings_dollars %}
        <a href="{{record.url}}"><strong class="on-sale">{{ record.name }}</strong></a>
        {% else %}
        <a href="{{record.url}}"><strong>{{ record.name }}</strong></a>
        {% endif %}
    """, verbose_name="Product")

    actions = tables.TemplateColumn("""
    <div class="columns">
        <div class="column">
            <button class="button show-update-url-modal is-small is-info is-light js-modal-trigger" data-target="modal-js-update-product-url" data-product-id="{{record.id}}" data-product-url="{{record.url}}">
                Update URL
            </button>
        </div>

        <div class="column">
            <form action="/product/delete" method="POST"">
                {% csrf_token %}
                <button hx-post="/product/delete" hx-target="#row-for-product-{{record.id}}" hx-swap="outerHTML" hx-confirm="Are you sure you want to remove this product?" name="remove" value="Remove" class="button is-danger is-small is-light">Remove</button>
                <input type="hidden" name="product_id" value={{record.id}}>
            </form>
        </div>

    </div>
    """)


    class Meta:
        model = Product
        orderable = False

        fields = ('name', 'sale_status', 'price', 'was_price', 'savings_percentage', 'savings_dollars', 'shop', 'last_price_check')
        sequence = ('image', 'name', 'shop', 'sale_status', 'price', 'was_price', 'savings_percentage', 'savings_dollars', 'last_price_check')

        attrs = {"class": "", "id": "products-table"}
        row_attrs = {
            "data-product-id": lambda record: record.pk,
            "id": lambda record: "row-for-product-" + str(record.pk),
        }