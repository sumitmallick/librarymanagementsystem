# Generated by Django 4.1.13 on 2024-04-27 06:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Books',
            new_name='Book',
        ),
        migrations.RenameModel(
            old_name='Members',
            new_name='Member',
        ),
    ]
