# Generated by Django 2.1.1 on 2018-10-25 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usercontent', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='venue',
            new_name='venue_id',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='venue',
            new_name='venue_id',
        ),
    ]
