# Generated by Django 4.0.6 on 2022-08-10 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_tracker', '0009_product_dummy_field_two'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='dummy_field',
        ),
        migrations.RemoveField(
            model_name='product',
            name='dummy_field_two',
        ),
    ]
