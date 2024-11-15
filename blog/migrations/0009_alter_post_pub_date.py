# Generated by Django 4.2 on 2024-10-31 12:15

import django.utils.timezone
from django.db import migrations, models

import blog.validators


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_alter_post_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text='Если установить дату и время в будущем — можно делать отложенные публикации.', null=True, validators=[blog.validators.date_in_future], verbose_name='Дата публикации'),
        ),
    ]
