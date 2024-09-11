# Generated by Django 5.1.1 on 2024-09-11 05:04

import django_fsm
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sales_orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="salesorder",
            name="state",
            field=django_fsm.FSMField(
                choices=[("unfinish", "未完成"), ("finished", "完成")],
                default="unfinish",
                max_length=50,
                protected=True,
            ),
        ),
    ]
