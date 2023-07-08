# Generated by Django 3.2 on 2023-07-08 10:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20230707_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredientsmerge',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Количество не может бытьменьше 1')], verbose_name='Количество'),
        ),
    ]
