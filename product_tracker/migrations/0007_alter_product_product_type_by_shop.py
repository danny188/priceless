# Generated by Django 4.0.6 on 2022-08-10 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_tracker', '0006_product_sale_notified_to_user_alter_product_shop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_type_by_shop',
            field=models.CharField(max_length=300),
        ),
    ]
