# Generated by Django 3.2.25 on 2024-06-26 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_auto_20240625_1300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='available_dates',
        ),
        migrations.AlterField(
            model_name='service',
            name='available_times',
            field=models.JSONField(default=list),
        ),
    ]