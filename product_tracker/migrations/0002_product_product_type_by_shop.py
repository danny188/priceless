# Generated by Django 4.0.6 on 2022-07-24 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_type_by_shop',
            field=models.CharField(default='WoolworthsProduct', max_length=200),
            preserve_default=False,
        ),
    ]