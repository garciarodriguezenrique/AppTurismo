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
                time.sleep(5)  # Wait for 5 seconds before re-trying
        return Response("error : Request failed", status=r.status_code)


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
            final_qs = check_cache(radius, category.split(","), LatLng)
            if final_qs:
                serializer = self.serializer_class(final_qs, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("ZERO_RESULTS", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("ERROR : Bad Request", status=status.HTTP_400_BAD_REQUEST)

def check_cache(radius, category_list, LatLng):
    radius_km = float(radius)/1000
    qs = PointOfInterest.objects.within_distance(float(LatLng.split(",")[0]),float(LatLng.split(",")[1])).filter(distance__lte=radius_km)
    final_qs = PointOfInterest.objects.none()
    for cat in category_list:
        aux = qs.filter(category__contains=cat)
        if len(aux)<5:
            make_asyncronous_request(CATEGORIES[cat], LatLng, radius)
            qs = PointOfInterest.objects.within_distance(float(LatLng.split(",")[0]),float(LatLng.split(",")[1])).filter(distance__lte=radius_km)
            aux = qs.filter(category__contains=cat)  
        final_qs = final_qs | aux
    return final_qs

def make_asyncronous_request(category_list, LatLng, radius):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&type={}&key="+KEY
    alt_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&location="+LatLng.split(",")[0]+","+LatLng.split(",")[1]+"&radius="+radius+"&key="+KEY
    print(url)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(url, alt_url, category_list))
    data = loop.run_until_complete(future)
    
    if 'results' in data:
        for element in data['results']:
            rating = "0.0"
            element['lat'] = element['geometry']['location']['lat']
            element['lng'] = element['geometry']['location']['lng']
            if 'rating' in element:
                rating = element['rating']
            #--------------------------------------------------------------------
            if 'vicinity' in element:
                if len(element['vicinity'])<12:
                    addr_resp = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(element['lat'])+","+str(element['lng'])+"&key="+KEY)
                    if addr_resp.ok:
                        element['vicinity']=addr_resp.json()['results'][1]['formatted_address']
            elif 'formatted_address' in element:
                if len(element['formatted_address'])<12:
                    addr_resp = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(element['lat'])+","+str(element['lng'])+"&key="+KEY)
                    if addr_resp.ok:
                        element['formatted_address']=addr_resp.json()['results'][1]['formatted_address']
                
            #--------------------------------------------------------------------
            if not PointOfInterest.objects.filter(reference=element['reference']):
                if not 'vicinity' in element:
                    poi = PointOfInterest(venue_id=element['id'], reference=element['reference'], formatted_address=element['formatted_address'], venue_name=element['name'], lat=element['lat'], lng=element['lng'], icon=element['icon'], rating=rating, category=["culture","monument"])
                    poi.save()
                else: 
                    poi = PointOfInterest(venue_id=element['id'], reference=element['reference'], formatted_address=element['vicinity'], venue_name=element['name'], lat=element['lat'], lng=element['lng'], icon=element['icon'], rating=rating, category=evaluate_types(element['types']))
                    poi.save()

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


async def run(url, alt_url, category_list):
    
    tasks = []

    async with ClientSession() as session:
        for i in category_list:
            if i=="hotel" or i=="monument":
                task = asyncio.ensure_future(fetch(alt_url.format(i), session))
            else:
                task = asyncio.ensure_future(fetch(url.format(i), session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        responses_clean = [x for x in responses if x is not None]

        if responses_clean:
            data = responses_clean[0]
            for item in responses_clean[1:]:
                data['results'].extend(item['results'])
            return data
        else:
            return responses_clean









