import django_tables2 as tables
from .models import *
import django.contrib.humanize.templatetags.humanize as humanize

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
    product_type_by_shop = tables.TemplateColumn("${{ record.savings_dollars }}", verbose_name="Shop")
    last_price_check = tables.Column()
    shop = tables.TemplateColumn('<a href="{{ record.get_shop_base_url }}"><img src="{{ record.get_shop_favicon_url }}"></a>')


    def render_last_price_check(self, value):
        return humanize.naturaltime(value)

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
            <button class="button refresh-product is-small is-info is-light" data-product-id="{{record.id}}">
                Check Price
            </button>
        </div>

        <!-- currently button not in use
        <div class="column">
            <button class="button show-update-url-modal is-small is-info is-light js-modal-trigger" data-target="modal-js-update-product-url" data-product-id="{{record.id}}" data-product-url="{{record.url}}">
                Update URL
            </button>
        </div>
        -->

        <div class="column">
            <form id="form-delete-product-{{record.id}}" action="/product/delete" method="POST"">
                {% csrf_token %}
                <button type="button" name="remove" value="Remove" class="button is-danger is-small is-light remove-product-button" data-product-id="{{record.id}}">Remove</button>
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


class ProductTableForEmail(tables.Table):
    image = tables.TemplateColumn("""
    {% if record.image_url %}
    <a href="{{record.url}}">
    <img src={{ record.image_url }}>
    </a>
    {% endif %}
    """, verbose_name='')

    price = tables.TemplateColumn("${{ record.current_price }}")
    was_price = tables.TemplateColumn("${{ record.was_price }}", verbose_name="Old Price")
    savings_percentage = tables.TemplateColumn("{{ record.savings_percentage }}%", verbose_name="Savings %")
    last_price_check = tables.TemplateColumn("{{ record.last_price_check|date:'Y-m-d H:i' }}")

    name = tables.TemplateColumn("""
        <a href="{{record.url}}"><strong>{{ record.name }}</strong></a>
    """, verbose_name="Product")

    class Meta:
        model = Product
        orderable = False

        fields = ('name', 'price', 'was_price', 'savings_percentage', 'shop', 'last_price_check')
        sequence = ('image', 'name', 'shop', 'price', 'was_price', 'savings_percentage', 'last_price_check')

        attrs = {"border": "1", "style": "border-color: grey; border-collapse:collapse; padding: 5px;",
                  'td': {'style': 'padding: 5px;'}}