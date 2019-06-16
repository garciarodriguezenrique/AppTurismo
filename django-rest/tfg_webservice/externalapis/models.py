from django.db import models
from django.conf import settings
from django.db.models import Func, F
from django_mysql.models import ListCharField


# Manager class used to query DB for PointsOfInterest within a given area
class DistanceManager(models.Manager):
    def within_distance(self, latitude, longitude):
        
        class Sin(Func):
            function = 'SIN'
        class Cos(Func):
            function = 'COS'
        class Acos(Func):
            function = 'ACOS'
        class Radians(Func):
            function = 'RADIANS'

        radlat = Radians(latitude) 
        radlong = Radians(longitude) 
        radflat = Radians(F('lat'))
        radflong = Radians(F('lng'))

        Expression = 6371 * Acos(Cos(radlat) * Cos(radflat) *
                                   Cos(radflong - radlong) +
                                   Sin(radlat) * Sin(radflat))

        return self.get_queryset()\
            .exclude(lat=None)\
            .exclude(lng=None)\
            .annotate(distance=Expression)

class PointOfInterest(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    venue_id = models.CharField(max_length=100, blank=True, default='')
    reference = models.CharField(max_length=100, blank=True, default='')
    formatted_address = models.CharField(max_length=200, blank=True, default='')
    rating = models.CharField(max_length=20, blank=True, default='')
    venue_name = models.CharField(max_length=100, blank=True, default='')
    category = ListCharField(
        base_field=models.CharField(max_length=20),
        size=13,
        max_length=(13 * 21) 
    )
    venue_id = models.CharField(max_length=100, blank=True, default='')
    icon = models.CharField(max_length=100, blank=True, default='')
    lat = models.DecimalField(max_digits=19, decimal_places=10, null=True)
    lng = models.DecimalField(max_digits=19, decimal_places=10, null=True)

    objects = DistanceManager()
    
    
    class Meta:
        ordering = ('created',)

