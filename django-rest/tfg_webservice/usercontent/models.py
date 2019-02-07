from django.db import models
from django.conf import settings

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    venue_id = models.CharField(max_length=100, blank=True, default='')
    
    class Meta:
        ordering = ('created',)

class Image(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='images', on_delete=models.CASCADE)
    caption = models.TextField()
    image = models.ImageField(upload_to='images/', max_length=254, blank=False)
    venue_id = models.CharField(max_length=100, blank=True, default='')
    
    class Meta:
        ordering = ('created',)

class Rating(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    avg_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    review_number = models.IntegerField()
    venue_id = models.CharField(max_length=100, blank=True, default='', primary_key=True)

    class Meta:
        ordering = ('created',)


