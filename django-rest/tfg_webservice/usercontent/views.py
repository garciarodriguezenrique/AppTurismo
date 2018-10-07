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
        venue = self.request.query_params.get('venue')
        user = self.request.query_params.get('user')
        if user is not None:
            queryset = queryset.filter(owner=self.request.user)
        else:
            queryset = queryset.filter(venue=venue)
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
        venue = self.request.query_params.get('venue')
        user = self.request.query_params.get('user')
        if user is not None:
            queryset = queryset.filter(owner=self.request.user)
        else:
            queryset = queryset.filter(venue=venue)
   
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


MAX_RETRIES = 3 #Max number of attemps to retrieve whatever data from a given external API

class ExternalAPI(APIView):
    
    def get(self, request, format=None):
        attempts = 0
        while attempts < MAX_RETRIES:
            r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=43.4917400,-8.2006500&radius=1500&type=restaurant&key=AIzaSyD5k4YFA5vGzVTaR0EvHRLEAVdhN0GV__s", timeout=10)
            if r.status_code == 200:
                data = r.json()
                return Response(data, status=status.HTTP_200_OK)
            else:
                attempt_num += 1
                # Should probably log this error using logger
                time.sleep(5)  # Wait for 5 seconds before re-trying
        return Response("error : Request failed", status=r.status_code)









