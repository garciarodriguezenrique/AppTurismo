from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
import requests
import time

KEY = "AIzaSyDEDOKsldYBl9NQ6Ml9uYVGOW2vosygeSs"
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

class ExternalAPI_getplacedetail(APIView):
    
    def get(self, request, place_id, format=None):
        attempts = 0
        while attempts < MAX_RETRIES:
            r = requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid="+place_id+"&fields=name,rating,formatted_address,type,opening_hours,website,formatted_phone_number&key="+KEY, timeout=10)
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
        attempts_next = 0
        total_results = []
        LatLng = self.request.query_params.get('LatLng', None)
        radius = self.request.query_params.get('radius', None)
        category = self.request.query_params.get('category', None)
        
        if LatLng and radius:
            while attempts < MAX_RETRIES:
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&type="+category+"&key="+KEY
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    # Pagination ------------------------------------------------------------------------------------------------------------------
                    while "next_page_token" in data:
                        time.sleep(2) #Wait for pagetoken to be valid.
                        total_results.extend(data["results"])
                        next_url = url+"&pagetoken="+data["next_page_token"]
                        r = requests.get(next_url, timeout=10)
                        if r.status_code == 200:
                            data = r.json()
                            total_results.extend(data["results"])
                        else:
                            return Response("error : Request failed", status=r.status_code)
                    data["results"] = total_results
                    # Pagination ------------------------------------------------------------------------------------------------------------------
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    attempts += 1
                    # Should probably log this error using logger
                    time.sleep(5)  # Wait for 5 seconds before re-trying
            return Response("error : Request failed", status=r.status_code)
        else:
            return Response("ERROR : Bad Request", status=status.HTTP_400_BAD_REQUEST)






