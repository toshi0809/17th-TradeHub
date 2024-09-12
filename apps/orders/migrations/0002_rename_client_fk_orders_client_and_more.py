# Generated by Django 5.1.1 on 2024-09-12 03:43

import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orders",
            old_name="client_fk",
            new_name="client",
        ),
        migrations.RenameField(
            model_name="orders",
            old_name="product_fk",
            new_name="product",
        ),
        migrations.AddField(
            model_name="orders",
            name="state",
            field=django_fsm.FSMField(
                choices=[("unfinish", "未完成"), ("finished", "完成")],
                default="unfinish",
                max_length=50,
                protected=True,
            ),
        ),
        migrations.AlterField(
            model_name="orders",
            name="note",
            field=models.TextField(blank=True, null=True),
        ),
    ]
