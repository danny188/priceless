from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    PRODUCT_SUMMARY_EMAIL_DAY_OF_WEEK_CHOICES = [('mon', 'Monday'),
                                                ('tue', 'Tuesday'),
                                                ('wed', 'Wednesday'),
                                                ('thu', 'Thursday'),
                                                ('fri', 'Friday'),
                                                ('sat', 'Saturday'),
                                                ('sun', 'Sunday'),]

    receive_email_as_products_go_on_sale = models.BooleanField(default=True)
    receive_product_sale_summary_email = models.BooleanField(default=True, verbose_name="Receive weekly product sale summary email")

    product_sale_summary_email_day_of_week = models.CharField(verbose_name="Day of week to receive product sale summary email", max_length=3, choices=PRODUCT_SUMMARY_EMAIL_DAY_OF_WEEK_CHOICES, default='fri')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
