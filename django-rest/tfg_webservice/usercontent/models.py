from django.db import models
from django.conf import settings

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    venue_id = models.CharField(max_length=100, blank=True, default='')
    
    class Meta:
        ordering = ('created',)

class Image(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', max_length=254, blank=False)
    caption = models.CharField(max_length=250, blank=True, default='')
    venue_id = models.CharField(max_length=100, blank=True, default='')
    
    class Meta:
        ordering = ('created',)


