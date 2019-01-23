from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from aiohttp import ClientSession
from externalapis.models import PointOfInterest, DistanceManager
from externalapis.serializers import PointOfInterestSerializer
from .categories import *
from .variables import KEY, MAX_RETRIES
import requests
import time
import asyncio
import copy

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

class ExternalAPI_getaddress(APIView):

    def get(self, request, format=None):
        LatLng = self.request.query_params.get('LatLng', None)
        attempts = 0
        while attempts < MAX_RETRIES:
            r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&key="+KEY)
            if r.ok:
                data = r.json()
                return Response(data, status=status.HTTP_200_OK)
            else:
                attempts += 1
                time.sleep(2)
        return Response("error : Request failed", status=r.status_code)

class ExternalAPI_getplacedetail(APIView):
    
    def get(self, request, place_id, format=None):
        attempts = 0
        while attempts < MAX_RETRIES:
            r = requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid="+place_id+"&fields=name,rating,formatted_address,type,opening_hours,geometry,website,formatted_phone_number&key="+KEY, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return Response(data, status=status.HTTP_200_OK)
            else:
                attempts += 1
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
        
        if LatLng and radius:
            while attempts < MAX_RETRIES:
                #url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&type="+category+"&key="+KEY  url vieja con campo types
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&key="+KEY
                print(url)
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
            return Response("error : Request failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("ERROR : Bad Request", status=status.HTTP_400_BAD_REQUEST)


class ExternalAPI_getvenues_async(APIView):
    serializer_class = PointOfInterestSerializer
    
    def get(self, request, format=None):
        attempts = 0
        attempts_next = 0
        total_results = []
        LatLng = self.request.query_params.get('LatLng', None)
        radius = self.request.query_params.get('radius', None)
        category = self.request.query_params.get('category', None)
        
        if LatLng and radius:
            #Comprobar si existen resultados cacheados para el area de la consulta
            final_qs = check_cache(radius, category.split(","), LatLng)
            if final_qs:
                serializer = self.serializer_class(final_qs, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("ZERO_RESULTS", status=status.HTTP_404_NOT_FOUND)
            #else:
            #    print("Not using cache")
                #url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&type="+category+"&key="+KEY  url vieja con campo types
            #    results = make_asyncronous_request(category_list, LatLng, radius)
            #    final_qs = check_cache(radius, category.split(","), LatLng)
            #    serializer = self.serializer_class(qs, many=True)
            #    return Response(serializer.data, status=status.HTTP_200_OK)
                #return Response(results, status=status.HTTP_200_OK)
        else:
            return Response("ERROR : Bad Request", status=status.HTTP_400_BAD_REQUEST)

#check_cache(radius, category.split(","))
def check_cache(radius, category_list, LatLng):
    radius_km = float(radius)/1000
    qs = PointOfInterest.objects.within_distance(float(LatLng.split(",")[0]),float(LatLng.split(",")[1])).filter(distance__lte=radius_km)
    final_qs = PointOfInterest.objects.none()
    for cat in category_list:
        print("Retrieving cached results for: "+cat)
        aux = qs.filter(category__contains=cat)
        if len(aux)<5:
            print("Not enough results for:"+cat+". Retrieving more...")
            results = make_asyncronous_request(CATEGORIES[cat], LatLng, radius)
            aux = qs.filter(category__contains=cat)       
        final_qs = final_qs | aux
    return final_qs

def make_asyncronous_request(category_list, LatLng, radius):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&type={}&key="+KEY
    print(url)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(url, category_list))
    data = loop.run_until_complete(future)
    #Cacheo de nuevos lugares
    if 'results' in data:
        for element in data['results']:
            rating = "0.0"
            element['lat'] = element['geometry']['location']['lat']
            element['lng'] = element['geometry']['location']['lng']
            if 'rating' in element:
                rating = element['rating']
            if not PointOfInterest.objects.filter(reference=element['reference']):
     
                poi = PointOfInterest(venue_id=element['id'], reference=element['reference'], formatted_address=element['vicinity'], venue_name=element['name'], lat=element['lat'], lng=element['lng'], icon=element['icon'], rating=rating, category=evaluate_types(element['types']))
                poi.save()
        return data['results']

def evaluate_types(types):
    categories=[]
    for category in CATEGORIES: 
        if any(t in CATEGORIES[category] for t in types):
            categories.append(category)
    return categories               


async def fetch(url, session):
    print(url)
    attempts = 0
    while attempts < MAX_RETRIES:
        async with session.get(url) as response:
            final_response = await response.json()
            #if final_response['status'] != 'ZERO_RESULTS':
            if final_response['status'] == 'OK':
                jData = final_response
                while 'next_page_token' in jData:
                    next_url = url+"&pagetoken="+jData['next_page_token']
                    time.sleep(1.5)
                    response = requests.get(next_url)
                    if response.status_code == 200:
                        jData = response.json()
                        final_response['results'].extend(jData['results'])
                    else:
                        attempts+=1
                        time.sleep(2)
                return final_response
            else:
                if final_response['status'] == 'ZERO_RESULTS':
                    attempts = MAX_RETRIES
                else:
                    attempts+=1
                    time.sleep(1)


async def run(url, category_list):
    
    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for i in category_list:
            task = asyncio.ensure_future(fetch(url.format(i), session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        responses_clean = [x for x in responses if x is not None]

        print("THIS IS RESPONSES CLEAN: \n")
        print(responses_clean)
        if responses_clean:
            # you now have all response bodies in this variable
            data = responses_clean[0]
            # for i in range(len(responses)):
            #    print(len(responses[i]['results']))
            for item in responses_clean[1:]:
                data['results'].extend(item['results'])
            return data
        else:
            return responses_clean









