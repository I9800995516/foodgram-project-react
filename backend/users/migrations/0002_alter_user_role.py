# Generated by Django 3.2 on 2023-07-01 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'user'), ('admin', 'admin')], default='user', max_length=15, verbose_name='Роль пользователя'),
        ),
    ]
