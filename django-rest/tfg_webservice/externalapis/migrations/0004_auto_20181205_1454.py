# Generated by Django 2.1.4 on 2018-12-05 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externalapis', '0003_auto_20181204_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='pointofinterest',
            name='category',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='pointofinterest',
            name='icon',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='pointofinterest',
            name='rating',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
