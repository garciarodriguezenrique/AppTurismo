# Generated by Django 2.1.4 on 2018-12-14 13:56

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usercontent', '0003_auto_20181214_1345'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CommentImage',
            new_name='Image',
        ),
    ]