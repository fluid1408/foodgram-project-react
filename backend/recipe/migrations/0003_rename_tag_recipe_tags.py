# Generated by Django 3.2.18 on 2023-03-29 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
    ]
