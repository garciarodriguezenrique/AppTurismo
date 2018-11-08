from rest_framework import serializers
from usercontent.models import Comment, Image
from django.contrib.auth.models import User

class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class CommentSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')
    venue_id = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ('text', 'venue_id', 'owner')

class ImageSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')
    venue_id = serializers.CharField(required=True)
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = Image
        fields = ('image', 'caption', 'venue_id', 'owner')

class UserSerializer(serializers.ModelSerializer):
    comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comment.objects.all())
    images = serializers.PrimaryKeyRelatedField(many=True, queryset=Image.objects.all())
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'comments', 'images')
