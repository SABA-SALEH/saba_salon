# Generated by Django 3.2.25 on 2024-07-26 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packages', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='services',
        ),
        migrations.AddField(
            model_name='package',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='packages/'),
        ),
    ]
