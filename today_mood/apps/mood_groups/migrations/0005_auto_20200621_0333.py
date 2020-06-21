# Generated by Django 3.0.3 on 2020-06-21 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mood_groups', '0004_auto_20200517_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='moodgroup',
            name='code',
            field=models.CharField(default=None, max_length=64, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='moodgroup',
            name='title',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
