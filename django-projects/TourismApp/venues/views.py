import requests
import json
import geocoder
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic, View
from .forms import SignupForm
from requests.auth import HTTPBasicAuth

PLACE_DETAIL_CACHE = {}

class SignUp(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class Index(View):
    template_name = 'venues/index.html'
    
    def get(self, request):
        context = {}
        return render(request, self.template_name, context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class PostNewComment(View):
    template = 'venues/detail.html'

    def post(self, request, place_id):
        print("ID:"+place_id)
        comment = request.POST["text"];
        
        url = "http://127.0.0.1:8000/comments/"

        response = requests.post(url, data = {'text':comment, 'venue_id': place_id}, auth = (request.user, 'password')) #Password is a placeholder, don't know how to retrieve the password of a given user
        if response.ok:
            #Once the new comment has been inserted in the DB, we retrieve the updated list of comments.
            r = requests.get(url+"?venue_id="+place_id)
            if r.ok:
                comments = json.loads(r.content.decode('utf-8'))
            else:
                comments = ""
            #Also retrieve images to reload detail page. (Should probably implement a cache for this, and for the comments in postImage)
            images_url = "http://127.0.0.1:8000/images/?venue_id="+place_id
            r = requests.get(images_url)
            if r.ok:
                images = json.loads(r.content.decode('utf-8'))
            else:
                images = "" #Images could not be retrieved
            #Retrieve details
            if place_id in PLACE_DETAIL_CACHE:
                details = PLACE_DETAIL_CACHE[place_id]
            else:
                #Make new request to Google Places. This should never happen, as to post new comments/images you must access a venue's detail page at which point its details will be cached.
                url="http://127.0.0.1:8000/external-api/getvenues/"+place_id
                response = requests.get(url)
                if response.ok:
                    details = json.loads(response.content.decode('utf-8'))
                else:
                    error_msg = str(response.status_code)+":"+response.reason
                    raise Exception(error_msg)
            name = details['result']['name']
            phone_number = details['result']['formatted_phone_number']
            address = details['result']['formatted_address']
            website = details['result']['website']
            schedule = details['result']['opening_hours']['weekday_text']
            categories = details['result']['types']
            context = {"comments":comments, 'images':images, 'name':name, 'phone_number':phone_number, 'addess':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id}
            return render(request, self.template_name, context)
        else:
            error_msg = str(response.status_code)+":"+response.reason
            raise Exception(error_msg)
        

class PostNewImage(View):
    template = 'venues/detail.html'

    def post(self, request, place_id):
        print("ID:"+place_id)
        image = request.POST["image"]
        caption = request.POST["caption"]
        
        url = "http://127.0.0.1:8000/images/"

        response = requests.post(url, data = {'image':image, 'caption':caption, 'venue_id': place_id}, auth = (request.user, 'password')) #Password is a placeholder, don't know how to retrieve the password of a given user
        if response.ok:
            #Once the new comment has been inserted in the DB, we retrieve the updated list of images.
            r = requests.get(url+"?venue_id="+place_id)
            if r.ok:
                images = json.loads(r.content.decode('utf-8'))
            else:
                images = "" #Images could not be retrieved
            #Also retrieve comments to reload detail page. (Should probably implement a cache for this, and for the images in postComment)
            comments_url = "http://127.0.0.1:8000/comments/?venue_id="+place_id
            r = requests.get(comments_url)
            if r.ok:
                comments = json.loads(r.content.decode('utf-8'))
            else:
                comments = "" #Comments could not be retrieved
            #Retrieve details
            if place_id in PLACE_DETAIL_CACHE:
                details = PLACE_DETAIL_CACHE[place_id]
            else:
                #Make new request to Google Places. This should never happen, as to post new comments/images you must access a venue's detail page at which point its details will be cached.
                url="http://127.0.0.1:8000/external-api/getvenues/"+place_id
                response = requests.get(url)
                if response.ok:
                    details = json.loads(response.content.decode('utf-8'))
                else:
                    error_msg = str(response.status_code)+":"+response.reason
                    raise Exception(error_msg)
            name = details['result']['name']
            phone_number = details['result']['formatted_phone_number']
            address = details['result']['formatted_address']
            website = details['result']['website']
            schedule = details['result']['opening_hours']['weekday_text']
            categories = details['result']['types']
            context = {'comments':comments, 'images':images, 'name':name, 'phone_number':phone_number, 'addess':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id}
            return render(request, self.template_name, context)
        else:
            error_msg = str(response.status_code)+":"+response.reason
            raise Exception(error_msg)

class Detail(View):
    template_name = 'venues/detail.html'

    def get(self, request, place_id):
        url="http://127.0.0.1:8000/external-api/getvenues/"+place_id
        response = requests.get(url)

        #Retrieve venue details
        if response.ok:
            jData = json.loads(response.content.decode('utf-8'))
            #Retrieve user comments
            comments_url = "http://127.0.0.1:8000/comments/?venue_id="+place_id
            r = requests.get(url)
            if r.ok:
                comments = json.loads(r.content.decode('utf-8'))
            else:
                comments = "" #Comments could not be retrieved
            #Retrieve user images
            images_url = "http://127.0.0.1:8000/images/?venue_id="+place_id
            r = requests.get(url)
            if r.ok:
                images = json.loads(r.content.decode('utf-8'))
            else:
                images = "" #Images could not be retrieved
            PLACE_DETAIL_CACHE[place_id] = jData 
            name = jData['result']['name']
            phone_number = jData['result']['formatted_phone_number']
            address = jData['result']['formatted_address']
            website = jData['result']['website']
            schedule = jData['result']['opening_hours']['weekday_text']
            categories = jData['result']['types']
            context = {'name':name, 'phone_number':phone_number, 'addess':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id, 'comments':comments, 'images':images}
            return render(request, self.template_name, context)
        else:
            error_msg = str(response.status_code)+":"+response.reason
            raise Exception(error_msg)

class Mapview(View):
    template_name = 'venues/mapview.html'

    def post(self, request):
        travel_mode = request.POST['travel_mode']
        radius = request.POST['radius']
        category = request.POST['category']
        client_ip = get_client_ip(request)
        myloc = geocoder.ip("me") #Necesario durante las pruebas (recupera mi dirección ip pública), cuando la aplicación se despliegue hay que cambiarlo por client_ip, si no obtendrá la ubicación de la máquina en la que corre la aplicación.
        
        if myloc is not None:
            user_coordinates = {'lat': myloc.lat, 'long': myloc.lng}
            print(user_coordinates)
            url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s&category=%s" % (user_coordinates['lat'],user_coordinates['long'],radius, category)
            print(url)
            response = requests.get(url)
        else:
            raise Exception("Geolocation data for your current position could not be retrieved.")

        if response.ok:
            print("Response is ok")
            jData = json.loads(response.content.decode('utf-8'))
            #Campos de la respuesta que queremos integrar en el DataFrame
            required_keys = ["name", "geometry", "id", "opening_hours", "price_level", "rating"]
            df = pd.DataFrame(jData['results'])[required_keys]

            #Limpieza de caracteres conflictivos
            df["name"] = df["name"].apply(lambda x: x.replace("'",""))
            df['opening_hours'] = df['opening_hours'].apply(pd.Series)['open_now'] #Extrae el valor de la clave anidada 'open_now'
            df = df.fillna(0) #Cambia los valores NaN por 0
            #Filtrado de valores booleanos para sustituirlos por String-----------------------
            mask = df.applymap(type) != bool
            replacement_dict = {True: 'Abierto', False: 'Cerrado'}
            df = df.where(mask, df.replace(replacement_dict))
            #---------------------------------------------------------------------------------
            d = df.to_json(orient='records')
            venues = json.loads(d)
            user_coordinates_json = json.loads(json.dumps(user_coordinates))
            context = {'venues':venues, 'user_location': user_coordinates_json, 'travel_mode': travel_mode}
            return render(request, self.template_name, context)
        else:
            error_msg = str(response.status_code)+":"+response.reason
            raise Exception(error_msg)


        #context = {'travel_mode':travel_mode, 'radius':radius, 'category':category, 'request':request}
        #return render(request, self.template_name, context)




