# Generated by Django 3.0.3 on 2020-03-15 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermood',
            name='created',
            field=models.DateTimeField(blank=True, db_index=True, editable=False, verbose_name='created date'),
        ),
    ]
