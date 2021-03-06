# Generated by Django 3.0.3 on 2020-03-10 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_auto_20200310_1249'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, 'soso'), (1, 'good'), (2, 'best'), (3, 'bad'), (4, 'worst')], verbose_name='status')),
                ('simple_summary', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name': 'mood',
            },
        ),
        migrations.CreateModel(
            name='UserMood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False, verbose_name='created date')),
                ('modified', models.DateTimeField(blank=True, editable=False, verbose_name='modified date')),
                ('mood', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moods.Mood')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.User')),
            ],
            options={
                'verbose_name': 'user_mood',
            },
        ),
    ]
