# Generated by Django 4.0.6 on 2022-07-24 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_tracker', '0002_product_product_type_by_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='shop',
            field=models.CharField(default='Woolworths', max_length=200),
            preserve_default=False,
        ),
    ]
