# Generated by Django 5.1.1 on 2024-09-20 17:36

import django_fsm
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inventory",
            name="state",
            field=django_fsm.FSMField(
                choices=[
                    ("out_stock", "缺貨"),
                    ("low_stock", "低於安全庫存量"),
                    ("normal", "正常"),
                    ("new_stock", "新庫存"),
                ],
                default="normal",
                max_length=50,
                protected=True,
            ),
        ),
    ]
