from django.contrib import admin
from usercontent.models import Comment, Rating, Image

# Register your models here.

admin.site.register(Comment)
admin.site.register(Image)
admin.site.register(Rating)
