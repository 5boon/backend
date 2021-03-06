# Generated by Django 3.0.3 on 2020-05-15 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moods', '0005_auto_20200402_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='mood',
            name='is_day_last',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='mood',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'worst'), (5, 'bad'), (10, 'mope'), (15, 'soso'), (20, 'good'), (25, 'best')], verbose_name='status'),
        ),
    ]
