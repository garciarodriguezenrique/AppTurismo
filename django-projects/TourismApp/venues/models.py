from django.db import models

# Create your models here.

class ImageUploadForm(models.Model):
    caption = models.CharField(max_length=250)
    image = models.ImageField()
