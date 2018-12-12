from rest_framework import serializers
from externalapis.models import PointOfInterest


class PointOfInterestSerializer(serializers.ModelSerializer):

    venue_id = serializers.CharField(required=True)
    reference = serializers.CharField(required=True)
    rating = serializers.CharField(required=True)
    venue_name = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    icon = serializers.CharField(required=True)
    #coordinates = serializers.CharField(required=True)
    lat = serializers.DecimalField(required=True, max_digits=19, decimal_places=10)
    lng = serializers.DecimalField(required=True, max_digits=19, decimal_places=10)

    class Meta:
        model = PointOfInterest
        fields = ('venue_id', 'reference', 'venue_name', 'lat', 'lng', 'category', 'rating', 'icon')
