# Generated by Django 3.2.25 on 2024-07-04 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('services', '0004_auto_20240626_1617'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('saving_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('services', models.ManyToManyField(related_name='packages', to='services.Service')),
            ],
        ),
    ]