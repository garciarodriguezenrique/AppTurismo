from usercontent.models import Comment, Image
from usercontent.permissions import IsOwnerOrReadOnly
from usercontent.serializers import CommentSerializer, ImageSerializer, UserSerializer
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
import requests
import time



class CommentList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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

class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

        
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer











