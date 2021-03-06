# Generated by Django 3.0.3 on 2020-03-29 16:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('moods', '0003_mood_do_show_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermood',
            name='created',
            field=models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created date'),
        ),
        migrations.AlterField(
            model_name='usermood',
            name='modified',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, verbose_name='modified date'),
        ),
    ]
