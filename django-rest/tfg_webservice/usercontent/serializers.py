from rest_framework import serializers
from usercontent.models import Comment, Image
from django.contrib.auth.models import User

class CommentSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')
    venue_id = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ('text', 'venue_id', 'owner')

class ImageSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')
    venue_id = serializers.CharField(required=True)

    class Meta:
        model = Image
        fields = ('image', 'caption', 'venue_id', 'owner')

class UserSerializer(serializers.ModelSerializer):
    comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comment.objects.all())
    images = serializers.PrimaryKeyRelatedField(many=True, queryset=Image.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'comments', 'images')
