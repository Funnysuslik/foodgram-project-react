# Generated by Django 4.1.4 on 2023-01-11 10:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_recipe_options_rename_created_recipe_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, validators=[django.core.validators.RegexValidator('^[-a-zA-Z0-9_]+$')]),
        ),
    ]