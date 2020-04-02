# Generated by Django 3.0.3 on 2020-04-02 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mood_groups', '0003_moodgroupinvitation'),
        ('moods', '0004_auto_20200329_1652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mood',
            name='do_show_summary',
        ),
        migrations.AddField(
            model_name='usermood',
            name='do_show_summary',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='usermood',
            name='mood_group',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='mood_groups.MoodGroup'),
        ),
    ]
