from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
import requests
import time

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

class ExternalAPI_getvenues(APIView):
    
    def get(self, request, format=None):
        attempts = 0
        total_results = []
        LatLng = self.request.query_params.get('LatLng', None)
        radius = self.request.query_params.get('radius', None)
        #category = self.request.query_params.get('category', None)
        #travel_mode = self.request.query_params.get('travel_mode', None)
        if LatLng and radius:
            while attempts < MAX_RETRIES:
                r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&type=restaurant&key=AIzaSyD5k4YFA5vGzVTaR0EvHRLEAVdhN0GV__s", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    # Pagination ------------------------------------------------------------------------------------------------------------------
                    total_results.extend(data["results"])
                    while "next_page_token" in data:
                        while attempts < MAX_RETRIES:
                            r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&type=restaurant&key=AIzaSyD5k4YFA5vGzVTaR0EvHRLEAVdhN0GV__s&pagetoken"+data["next_page_token"], timeout=10)
                            if r.status_code == 200:
                                data = r.json()
                                total_results.extend(data["results"])
                    data["results"] = total_results
                    # Pagination ------------------------------------------------------------------------------------------------------------------
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    attempt_num += 1
                    # Should probably log this error using logger
                    time.sleep(5)  # Wait for 5 seconds before re-trying
            return Response("error : Request failed", status=r.status_code)
        else:
            return Response("ERROR : Bad Request", status=status.HTTP_400_BAD_REQUEST)

class ExternalAPI_getmap(APIView):

    def get(self, request, format=None):
        attempts = 0
        map_code = "<!DOCTYPE html><html><head><title>Simple Map</title><meta name=\"viewport\" content=\"initial-scale=1.0\"><meta charset=\"utf-8\"><style>/* Always set the map height explicitly to define the size of the div* element that contains the map. */#map {height: 100%;}/* Optional: Makes the sample page fill the window. */html, body {height: 100%;margin: 0;padding: 0;}</style></head><body><div id=\"map\"></div><script>var map;function initMap() {map = new google.maps.Map(document.getElementById('map'), {center: {lat: -34.397, lng: 150.644},zoom: 8});}</script><script src=\"https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap\"async defer></script></body></html>"
        #map_source = 
        return Response("error : Request failed", status=r.status_code)



