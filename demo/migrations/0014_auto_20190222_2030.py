# Generated by Django 2.1 on 2019-02-22 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0013_information_head'),
    ]

    operations = [
        migrations.RenameField(
            model_name='information',
            old_name='head',
            new_name='title',
        ),
    ]
