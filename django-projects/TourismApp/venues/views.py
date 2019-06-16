import requests
import json
import geocoder
import base64
import bleach
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from dateutil import parser
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import escape
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views import generic, View
from .forms import SignupForm, ImageUploadForm, AccModForm
from requests.auth import HTTPBasicAuth
from .categories import *
from .webservice_endpoints import *
from .variables import R, request_radius, days_es

#------------------------------------------------------------------------------------#
# Vista de eliminación de usuario.                                                   #
#                                                                                    #
# Gestiona el borrado de usuarios en la BD del servicio web                          #
#------------------------------------------------------------------------------------#

class DeleteAccount(View):
    template_name_on_success = 'venues/index-desktop.html'
    template_name_on_success_mobile = 'venues/index-mobile.html'
    template_name_on_error = 'venues/error-template.html'

    def get(self, request):
        print("deleting...")
        url = "http://127.0.0.1:8000/users/my_account/"
        response = requests.delete(url, headers = {'Authorization':'token '+request.session['auth_token']})

        if response.ok:
            context={}
            if request.user_agent.is_mobile:
                return render(request, self.template_on_success_mobile, context)
            else:
                return render(request, self.template_on_success, context)
        else:
            return render(request, self.template_name_on_error, {"No se ha podido eliminar la cuenta. Por favor, inténtalo más tarde."})

#------------------------------------------------------------------------------------#
# Vista de alta de usuario.                                                          #
#                                                                                    #
# Gestiona el renderizado de la página de sing-up y la creación de nuevos usuarios   #
# en la BD del servicio web                                                          #
#------------------------------------------------------------------------------------#

class SignUp(View):
    form_class = SignupForm
    template_name_on_success = 'venues/index-desktop.html'
    template_name_on_success_mobile = 'venues/index-mobile.html'
    template_name_on_login_error = 'registration/login.html'
    template_name_on_signup_error = 'registration/signup.html'
    template_name = 'registration/signup.html'

    def get(self, request):
        request.session['signup_from'] = request.META.get('HTTP_REFERER', '/')
        return render(request, self.template_name, {'form':self.form_class})
    

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = bleach.clean(form.cleaned_data.get('username'))
            raw_password = bleach.clean(form.cleaned_data.get('password1'))
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            data = {'username':username,'password':raw_password}
            response = requests.post(signup_endpoint, data)
            
            if response.ok:
                response = requests.post(login_endpoint, data = {'username':username,'password':raw_password})
                if response.ok:
                    token = response.json()['token']
                    request.session['auth_token'] = token
                    context = {}
                    if request.user_agent.is_mobile:
                        return render(request, self.template_name_on_success_mobile, context)
                    else:
                        return render(request, self.template_name_on_success, context)
                else:
                    messages.error(request,'El usuario no existe.')
                    context = {'form':AuthenticationForm}
                    return render(request, self.template_name_on_login_error, context)
            else:
                messages.error(request,'Algo salió mal al intentar crear tu cuenta. Inténtalo más tarde.')
                context = {'form':self.form_class}
                return render(request, self.template_name_on_signup_error, context)
        else:
            return render(request, self.template_name_on_signup_error, {'form':form})
                
           
#------------------------------------------------------------------------------------#
# Vista de cambio de contraseña.                                                     #
#                                                                                    #
# Gestiona el renderizado de la página de usuario y la modificación de las creden-   #
# ciales de los usuarios en la BD del servicio web                                   #
#------------------------------------------------------------------------------------#

class PasswordChange(View):
    template_name = 'registration/password_change.html'
    template_name_on_success = 'venues/index-desktop.html'
    template_name_on_success_mobile = 'venues/index-mobile.html'
    template_name_on_error = 'venues/error-template.html'
    form_class = AccModForm

    def get(self, request):
        return render(request, self.template_name, {'form':self.form_class})

    def post(self, request):
        url = "http://127.0.0.1:8000/users/my_account/"
        form = AccModForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=self.request.user)
            if user.check_password(request.POST['old_password']):
                response = requests.put(url, data={'password':bleach.clean(request.POST['password2'])}, headers = {'Authorization':'token '+request.session['auth_token']})
                if response.ok:
                    data = {'password':bleach.clean(request.POST['password2'])}
                    user.set_password(bleach.clean(request.POST['password1']))
                    user.save()
                    if request.user_agent.is_mobile:
                        return render(request, self.template_name_on_success_mobile, {})
                    else:
                        return render(request, self.template_name_on_success, {})
                else:
                    return render(request, self.template_name_on_error, {'error':"Ha habido un problema al intentar modificar la información de inicio de sesión. Por favor, inténtalo más tarde"})
            else:
                messages.error(request, "La contraseña actual introducida no es correcta")
                return render(request, self.template_name, {'form':self.form_class})
        else:
            return render(request, self.template_name, {'form':form})
            
#------------------------------------------------------------------------------------#
# Vista de inicio de sesión.                                                         #
#                                                                                    #
# Gestiona el renderizado de la página de log-in y la validación de las credencia-   #
# les de los usuarios contra el servicio web                                         #
#------------------------------------------------------------------------------------#

class Login(View):
    form_class = AuthenticationForm
    template_name_on_success = 'venues/index-desktop.html'
    template_name_on_success_mobile = 'venues/index-mobile.html'
    template_name_on_error = 'registration/login.html'
    template_name = 'registration/login.html'

    def get(self, request):
        print(request.META.get('HTTP_REFERER', '/'))
        request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
        return render(request, self.template_name, {'form':self.form_class})
    
    def post(self, request):
        username = bleach.clean(self.request.POST['username'])
        password = bleach.clean(self.request.POST['password'])
        if request.session['login_from']:
                    print("you logged from: "+request.session['login_from'])
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = requests.post(login_endpoint, data={'username':username, 'password':password})
            if response.ok:
                token = response.json()['token']
                request.session['auth_token'] = token
                context = {}
                if request.session['login_from']:
                    return HttpResponseRedirect(request.session['login_from'])
                else:
                    if request.user_agent.is_mobile:
                        return render(request, self.mobile_template_on_success_mobile, context)
                    else:
                        return render(request, self.template_name_on_success, context)
            else:
                messages.error(request,'Algo salió mal al intentar iniciar tu sesión. Inténtalo más tarde.')
                context = {'form':self.form_class}
                return render(request, self.template_name_on_error, context)
        else:
            messages.error(request,'Usuario o contraseña incorrectos')
            context = {'form':self.form_class}
            return render(request, self.template_name_on_error, context)
        


#------------------------------------------------------------------------------------#
# Vista índice.                                                                      #
#                                                                                    #
# Gestiona el renderizado de la página de inicio.                                    #
#------------------------------------------------------------------------------------#

class Index(View):
    template_name = 'venues/index-desktop.html'
    mobile_template = 'venues/index-mobile.html'
    
    def get(self, request):
        context = {}
        
        if request.user_agent.is_mobile:
            return render(request, self.mobile_template, context)
        else:
            return render(request, self.template_name, context)

        
#------------------------------------------------------------------------------------#
# Vista de detalle.                                                                  #
#                                                                                    #
# Gestiona la obtención de los detalles de un punto de interés a través del servicio #
# web, además del renderizado de la página de detalle                                #
#------------------------------------------------------------------------------------#

class Detail(View):
    template_name = 'venues/detail-desktop.html'
    mobile_template = 'venues/detail-mobile.html'
    template_name_on_error = 'venues/error-template.html'

    def get(self, request, place_id, content_page=''):
        image_list = []
        comment_list = []
        next = ""
        previous = ""
        url=external_services_endpoint+"getvenues/"+place_id
        print(url)
        response = requests.get(url)
        
        if response.ok:
            jData = json.loads(response.content.decode('utf-8'))
            
            phone_number = ""
            address = ""
            website = ""
            schedule = ""
            categories = ""
 
            name = jData['result']['name'].replace("_"," ")
            if 'formatted_phone_number' in jData['result']: 
                phone_number = jData['result']['formatted_phone_number']
            response_addr = requests.get(external_services_endpoint+"reverse-geocode/?LatLng="+str(jData['result']['geometry']['location']['lat'])+","+str(jData['result']['geometry']['location']['lng']))
            if response_addr.ok:
                data=response_addr.json()
                address = data['results'][1]['formatted_address']
            elif 'formatted_address' in jData['result']:
                address = jData['result']['formatted_address']
            else:
                address = ""
            if 'website' in jData['result']:
                website = jData['result']['website']
            if 'opening_hours' in jData['result'] and 'weekday_text' in jData['result']['opening_hours']:
                schedule = [day.replace(day.split(':')[0],days_es.get(day.split(':')[0])) for day in jData['result']['opening_hours']['weekday_text']]
                schedule = [day.replace("Closed","Cerrado") for day in schedule]
                schedule = [day.replace("Open","Abierto") for day in schedule]
            if 'types' in jData['result']:
                categories = jData['result']['types']

            context = {'name':name, 'phone_number':phone_number, 'address':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id}
            if request.user_agent.is_mobile:
                return render(request, self.mobile_template, context)
            else:
                return render(request, self.template_name, context)
        else: 
            error_msg = str(response.status_code)+":"+response.reason
            messages.error(request,error_msg)
            error = "No pudieron recuperarse los detalles de este sitio ("+error_msg+")"
            context = {'error':error}
            return render(request, self.template_name_on_error, context)

#------------------------------------------------------------------------------------#
#                                                                                    #
# Función auxiliar que realiza tareas de preparación y limpieza de caracteres        #
# conflictivos en la respuesta del servicio web                                      #
#                                                                                    #
#------------------------------------------------------------------------------------#

def cleanResponse(jData): 

            required_keys = ["venue_name", "lat", "venue_id", "rating", "reference", "category", "icon", "lng", "formatted_address"]

            df = pd.DataFrame(jData)[required_keys] 
            df["venue_name"] = df["venue_name"].apply(lambda x: x.replace("'",""))
            df["venue_name"] = df["venue_name"].apply(lambda x: x.replace("`",""))
            df["venue_name"] = df["venue_name"].apply(lambda x: x.replace("_"," "))
            df["formatted_address"] = df["formatted_address"].apply(lambda x: x.replace("'",""))
            df["formatted_address"] = df["formatted_address"].apply(lambda x: x.replace("`",""))
            df["formatted_address"] = df["formatted_address"].apply(lambda x: x.replace("_"," "))
            df = df.fillna(0) 
            d = df.to_json(orient='records')
            return d

#------------------------------------------------------------------------------------#
#                                                                                    #
# Función auxiliar que prepara el conjunto de categorías seleccionadas para          #
# incluírlas de manera que en la petición de búsqueda de manera que se ajusten       #
#al formato esperado por el servicio web.                                            #
#                                                                                    #
#------------------------------------------------------------------------------------#

def formatCategory(category):
    finalString = ""
    for element in category:
        finalString+=element+"|"
    return finalString[:-1]

#-------------------------------------------------------------------------------------------------#
# Vista de resultados.                                                                            #
#                                                                                                 #
# Obtiene información de los puntos de interés de la categoría seleccionada por el usuario y pre- #
# para está información para ser presentada. Gestiona también el renderizado de la página de      #
# resultados.                                                                                     #
#-------------------------------------------------------------------------------------------------#

class Mapview(View):
    template_name = 'venues/mapview_desktop.html'
    template_name_alt = 'venues/listview-mobile-alt.html'
    mobile_template = 'venues/listview-mobile.html'
    template_name_on_error = 'venues/error-template.html'

    def get(self, request):

        if request.session['user_coordinates'] and request.session['last_category']:
            venues = request.session['last_response']
            url=external_services_endpoint+"getvenues/?LatLng=%s,%s&radius=%s&category=%s" % (request.session['user_coordinates']['lat'], request.session['user_coordinates']['long'],request_radius, request.session['last_category']) 
            response = requests.get(url)
            if response.ok:
                jData = response.json()
                d = cleanResponse(jData)
                venues = json.loads(d)
                r = requests.get(rating_endpoint)
                if r.ok:
                    ratings = r.json()
                    aux_dict = {}
                    for rating in ratings['results']:
                        aux_dict[rating['venue_id']] = rating['avg_rating']
                    for venue in venues:
                        venue['dist_from_user'] = calcDistance(venue['lat'], venue['lng'], request) #R*c
                        if venue['reference'] in aux_dict:
                            venue['rating'] = aux_dict[venue['reference']]
                        else:
                            venue['rating'] = "0.00"
                user_coordinates_json = json.loads(json.dumps(request.session['user_coordinates']))
                category = request.session['last_category']
            else: 
                error_msg = str(response.status_code)+":"+response.reason
                error="Hubo un error al tratar de obtener puntos de interés cerca de tu ubicación ("+error_msg+")"
                if str(response.status_code) == "404":
                    error="No se han encontrado puntos de interés de la categoría especificada en el área."
                context = {'error':error}
                return render(request, self.template_name_on_error, context)
        else:
            error="Hubo un error al tratar de obtener puntos de interés cerca de tu ubicación"
            context = {'error':error}
            return render(request, self.template_name_on_error, context)

        
        context = {'venues':venues, 'user_location': user_coordinates_json, 'initial_category':category}
        if request.user_agent.is_mobile:
            return render(request, self.mobile_template, context)
        else:
            return render(request, self.template_name, context)

    def post(self, request):
       
        position = request.POST['position']
        category = request.POST['category']
        gps = request.POST['gps']
        request.session['last_category'] = category
        
        if position:
            user_coordinates = {'lat': float(position.split(",")[0]), 'long': float(position.split(",")[1])}
            request.session['user_coordinates'] = user_coordinates
            url=external_services_endpoint+"getvenues/?LatLng=%s,%s&radius=%s&category=%s" % (user_coordinates['lat'],user_coordinates['long'],request_radius, category) 
            print(url)
            response = requests.get(url)
        else:
            error = "Hubo un error al tratar de obtener tu ubicación."
            context = {'error':error}
            error = "Hubo un error al tratar de obtener tu ubicación."
            return render(request, self.template_name_on_error, context)

        if response.ok:
            jData = response.json()
            d = cleanResponse(jData)
            venues = json.loads(d)
            user_coordinates_json = json.loads(json.dumps(user_coordinates))
            r = requests.get(rating_endpoint)
            if r.ok:
                ratings = r.json()
                aux_dict = {}
                for rating in ratings['results']:
                    aux_dict[rating['venue_id']] = rating['avg_rating']
                for venue in venues:
                    venue['dist_from_user'] = calcDistance(venue['lat'], venue['lng'], request) #R*c
                    if venue['reference'] in aux_dict:
                        venue['rating'] = aux_dict[venue['reference']]
                    else:
                        venue['rating'] = "0.00"
            request.session['last_response'] = venues
            context = {'venues':venues, 'user_location': user_coordinates_json, 'initial_category':category}
           
            if request.user_agent.is_mobile:
                if gps=='false':
                    return render(request, self.template_name_alt, context)
                else:
                    return render(request, self.mobile_template, context)
            else:
                return render(request, self.template_name, context)
        else: 
            error_msg = str(response.status_code)+":"+response.reason
            error="Hubo un error al tratar de obtener puntos de interés cerca de tu ubicación ("+error_msg+")"
            if str(response.status_code) == "404":
                error="No se han encontrado puntos de interés de la categoría especificada en el área."
            context = {'error':error}
            return render(request, self.template_name_on_error, context)


#---------------------------------------------------------------------------------------------#
#                                                                                             #
# Las siguientes funciones se usan para actualizar las cajas de comentarios e imágenes de     #
# las páginas detalle, así como mantener actualizada la información relativa a la puntuación  #
# media según las valoraciones de los usuarios                                                #
#                                                                                             #
#---------------------------------------------------------------------------------------------#


class GetAvgRating(View):

    def get(self, request):
        place_id = request.GET['venue_id']
        url = rating_endpoint+"?venue_id="+place_id
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(500)

class NewComment(View):

    def post(self, request):
        place_id = request.GET['venue_id']
        comment = bleach.clean(request.POST["text"])
        rating = request.POST["rating"]
        image = None
        if "image" in request.FILES:
            stream = request.FILES["image"].file
            image = base64.b64encode(stream.getvalue())
        
        response = requests.post(comment_endpoint, data = {'text':comment, 'rating':rating, 'venue_id': place_id}, headers = {'Authorization':'token '+request.session['auth_token']}) 
        if response.ok:
            return HttpResponse(201)
        else:
            return HttpResponse(500)

class NewImage(View):

    def post(self, request):
        place_id = request.GET['venue_id']
        caption = bleach.clean(request.POST["caption"])
        image = None
        if "image" in request.FILES:
            stream = request.FILES["image"].file
            image = base64.b64encode(stream.getvalue())
        
        response = requests.post(image_endpoint, data = {'caption':caption, 'image':image, 'venue_id': place_id}, headers = {'Authorization':'token '+request.session['auth_token']}) 
        
        if response.ok:
            return HttpResponse(201)
        else:
            return HttpResponse(500)

class GetComments(View):

    def get(self, request):
        place_id = request.GET['venue_id']
        page = request.GET['page']
        comments_url = comment_endpoint+"?venue_id="+place_id
        if page and page!="1":
            comments_url = comment_endpoint+"?page="+page+"&venue_id="+place_id

        r = requests.get(comments_url)
        if r.ok:
            data = r.json()
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(500)

class GetImages(View):

    def get(self, request):
        place_id = request.GET['venue_id']
        page = request.GET['page']
        images_url = image_endpoint+"?venue_id="+place_id
        if page and page!="1":
            images_url = image_endpoint+"?page="+page+"&venue_id="+place_id

        r = requests.get(images_url)
        if r.ok:
            data = r.json()
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(500)

class RemoveComment(View):

    def get(self, request):
        comment_id = request.GET['comment_id']

        response = requests.delete(comment_endpoint+comment_id, headers = {'Authorization':'token '+request.session['auth_token']})

        if response.ok:
            return HttpResponse(204)
        else:
            return HttpResponse(500)

class RemoveImage(View):

    def get(self, request):
        image_id = request.GET['image_id']

        response = requests.delete(image_endpoint+image_id, headers = {'Authorization':'token '+request.session['auth_token']})

        if response.ok:
            return HttpResponse(204)
        else:
            return HttpResponse(500)

class ReverseGeocode(View):

    def get(self, request):
        LatLng = request.GET['LatLng']

        response = requests.get(external_services_endpoint+"reverse-geocode/?LatLng="+LatLng.split(",")[0]+","+LatLng.split(",")[1])

        if response.ok:
            data = response.json()
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(500)


def calcDistance(venue_lat, venue_lng, request):
    lat2 = radians(float(venue_lat))
    lon2 = radians(float(venue_lng))
    dlat = lat2 - radians(request.session['user_coordinates']['lat'])
    dlon = lon2 - radians(request.session['user_coordinates']['long'])
    a = sin(dlat / 2)**2 + cos(radians(request.session['user_coordinates']['lat'])) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R*c

#-------------------------------------------------------------------------------------------#
# Vista de búsqueda avanzada.                                                               #
#                                                                                           #
# Gestiona las operaciones de búsqueda avanzada invocadas desde la página de resultados     #
#-------------------------------------------------------------------------------------------#

class Filter(View):

    def get(self, request):
        categories = request.GET['category'].split("|")
        up = request.GET['user_position']
        user_coordinates = {'lat': float(up.split(",")[0]), 'long': float(up.split(",")[1])}
        request.session['user_coordinates'] = user_coordinates
        formattedCategories = ",".join(categories)
        request.session['last_category'] = formattedCategories

        url=external_services_endpoint+"getvenues/?LatLng=%s,%s&radius=%s&category=%s" % (user_coordinates['lat'],user_coordinates['long'],request_radius, formattedCategories)
        response = requests.get(url)

        if response.ok:
            jData = response.json()
            d = cleanResponse(jData)
            venues = json.loads(d)
            r = requests.get(rating_endpoint)
            if r.ok:
                ratings = r.json()
                aux_dict = {}
                for rating in ratings['results']:
                    aux_dict[rating['venue_id']] = rating['avg_rating']
                for venue in venues:
                    venue['dist_from_user'] = calcDistance(venue['lat'], venue['lng'], request) 
                    if venue['reference'] in aux_dict:
                        venue['rating'] = aux_dict[venue['reference']]
                    else:
                        venue['rating'] = "0.00"
            request.session['last_response'] = venues
            return HttpResponse(json.dumps(venues), content_type="application/json")
        elif response.json() == 'ZERO_RESULTS':
            return HttpResponse(status=404)
        else:
            return HttpResponse(status=500)
            
     

        



