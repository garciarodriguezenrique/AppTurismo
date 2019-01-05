from django.db import models
from django.conf import settings

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    #image = models.ForeignKey('Image', related_name='comments', on_delete=models.CASCADE, default=None)
    #image = models.ImageField(upload_to='images/', max_length=254, blank=False)
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

#class Image(models.Model):
#    created = models.DateTimeField(auto_now_add=True)
#    owner = models.ForeignKey('auth.User', related_name='images', on_delete=models.CASCADE)
#    image = models.ImageField(upload_to='images/', max_length=254, blank=False)

#    class Meta:
#        ordering = ('created',)

#class Image(models.Model):
#    created = models.DateTimeField(auto_now_add=True)
#    owner = models.ForeignKey('auth.User', related_name='images', on_delete=models.CASCADE)
#    image = models.ImageField(upload_to='images/', max_length=254, blank=False)
#    caption = models.CharField(max_length=250, blank=True, default='')
#    venue_id = models.CharField(max_length=100, blank=True, default='')
    
#    class Meta:
#        ordering = ('created',)


