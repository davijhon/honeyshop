# Generated by Django 5.0.6 on 2024-06-28 20:35

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("street_address", models.CharField(max_length=100)),
                ("apartment_address", models.CharField(max_length=100)),
                ("country", django_countries.fields.CountryField(max_length=2)),
                ("zip_code", models.CharField(max_length=100)),
                (
                    "address_type",
                    models.CharField(
                        choices=[("B", "Billing"), ("S", "Shipping")], max_length=1
                    ),
                ),
                ("default", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name_plural": "Addresses",
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=30)),
                ("description", models.CharField(max_length=200)),
                ("image", models.ImageField(blank=True, upload_to="images/")),
                ("slug", models.SlugField(max_length=200, unique=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "category",
                "verbose_name_plural": "categories",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ref_code", models.CharField(max_length=9)),
                ("start_date", models.DateTimeField(auto_now_add=True)),
                ("ordered_date", models.DateTimeField()),
                ("ordered", models.BooleanField(default=False)),
                (
                    "payment_option",
                    models.CharField(
                        choices=[("S", "Stripe"), ("P", "PayPal")], max_length=1
                    ),
                ),
                ("being_delivered", models.BooleanField(default=False)),
                ("received", models.BooleanField(default=False)),
                ("refund_request", models.BooleanField(default=False)),
                ("refund_granted", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ordered", models.BooleanField(default=False)),
                ("quantity", models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("charge_id", models.CharField(max_length=50)),
                ("amount", models.FloatField()),
                (
                    "payment_option",
                    models.CharField(
                        choices=[("S", "Stripe"), ("P", "PayPal")], max_length=1
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=200)),
                ("slug", models.SlugField(max_length=200)),
                ("image", models.ImageField(blank=True, upload_to="products/%Y/%m/%d")),
                ("description", models.TextField(blank=True)),
                ("price", models.FloatField()),
                ("quantity", models.IntegerField(default=1)),
                ("available", models.BooleanField(default=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Refund",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reason", models.TextField()),
                ("accepted", models.BooleanField(default=False)),
                ("email", models.EmailField(max_length=254)),
            ],
        ),
    ]
