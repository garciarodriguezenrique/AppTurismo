# Generated by Django 2.1.4 on 2019-01-05 19:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usercontent', '0006_auto_20190103_1834'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('caption', models.TextField()),
                ('image', models.ImageField(max_length=254, upload_to='images/')),
                ('venue_id', models.CharField(blank=True, default='', max_length=100)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.RemoveField(
            model_name='comment',
            name='image',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='id',
        ),
        migrations.AlterField(
            model_name='rating',
            name='venue_id',
            field=models.CharField(blank=True, default='', max_length=100, primary_key=True, serialize=False),
        ),
    ]