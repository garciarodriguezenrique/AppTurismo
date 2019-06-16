from usercontent.models import Comment, Rating, Image
from usercontent.permissions import IsOwnerOrReadOnly
from usercontent.serializers import CommentSerializer, UserSerializer, RatingSerializer, ImageSerializer
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Avg
import requests
import time

class RatingList(generics.ListAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_queryset(self):
        venue_id = self.request.query_params.get('venue_id')
        if venue_id is not None:
            queryset = Rating.objects.filter(venue_id=venue_id)
        else:
            queryset = Rating.objects.all()
        return queryset
        

class CommentList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        #Retrieve comments, compute avg rating and create/update a new Rating object.
        venue_id = self.request.data.get("venue_id")
        avg = Comment.objects.filter(venue_id=venue_id).aggregate(Avg('rating'))['rating__avg']
        num_reviews = Comment.objects.filter(venue_id=venue_id).count()
        rating = Rating(avg_rating=avg, review_number=num_reviews, venue_id=venue_id)
        rating.save()
             
    def get_queryset(self):
        queryset = Comment.objects.all()
        venue_id = self.request.query_params.get('venue_id')
        user = self.request.query_params.get('user')
        if user is not None:
            queryset = queryset.filter(owner=self.request.user)
        else:
            queryset = queryset.filter(venue_id=venue_id)
        return queryset

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_destroy(self, instance):
        serializer = CommentSerializer(instance)
        venue_id = serializer.data['venue_id']
        instance.delete()
        #Retrieve comments, compute avg rating and create/update a new Rating object.
        avg = Comment.objects.filter(venue_id=venue_id).aggregate(Avg('rating'))['rating__avg']
        num_reviews = Comment.objects.filter(venue_id=venue_id).count()
        rating = Rating(avg_rating=avg, review_number=num_reviews, venue_id=venue_id)
        rating.save()
        

class ImageList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = Image.objects.all()
        venue_id = self.request.query_params.get('venue_id')
        user = self.request.query_params.get('user')
        if user is not None:
            queryset = queryset.filter(owner=self.request.user)
        else:
            queryset = queryset.filter(venue_id=venue_id)
   
        return queryset

class Login(APIView):
    
    def post(self, request):
        username = self.request.data.get("username")
        password = self.request.data.get("password")
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'},
                            status=status.HTTP_404_NOT_FOUND)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key},
                        status=status.HTTP_200_OK)

class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

        
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserCreation(generics.CreateAPIView):
    model = User
    permission_classes = [
        permissions.AllowAny # Or else anon users can't register
    ]
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request):
        user = self.get_object()
        password = request.data.get("password")
        user.set_password(password)
        user.save()
        return Response(status=status.HTTP_200_OK)











