# Generated by Django 3.0.3 on 2020-04-02 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200310_1249'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='nickname',
            new_name='name',
        ),
    ]