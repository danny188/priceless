# Generated by Django 4.0.6 on 2022-08-08 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_email_alert_day_of_week'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='email_alert_day_of_week',
        ),
        migrations.RemoveField(
            model_name='user',
            name='email_alert_frequency',
        ),
        migrations.RemoveField(
            model_name='user',
            name='pause_email_alerts',
        ),
        migrations.AddField(
            model_name='user',
            name='product_sale_summary_email_day_of_week',
            field=models.CharField(choices=[('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'), ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')], default='fri', max_length=3, verbose_name='Day of week to receive product sale summary email'),
        ),
        migrations.AddField(
            model_name='user',
            name='receive_email_as_products_go_on_sale',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='receive_product_sale_summary_email',
            field=models.BooleanField(default=True),
        ),
    ]
