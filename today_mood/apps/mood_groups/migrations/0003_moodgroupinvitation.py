# Generated by Django 3.0.3 on 2020-04-02 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200402_1004'),
        ('mood_groups', '0002_auto_20200329_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoodGroupInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invited_by', models.CharField(max_length=50)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.User')),
                ('mood_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mood_groups.MoodGroup')),
            ],
            options={
                'verbose_name': 'user_mood_group',
            },
        ),
    ]
