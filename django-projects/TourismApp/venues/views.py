import requests
import json
import geocoder
import base64
import pandas as pd
from dateutil import parser
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views import generic, View
from .forms import SignupForm, ImageUploadForm
from requests.auth import HTTPBasicAuth

#Solución temporal para no repetir la petición de detalle cuando se envían comentarios o fotos.
PLACE_DETAIL_CACHE = {}

#Tipos de punto de interés (wrapper de las categorías de Google Places)
food=["restaurant","meal_delivery","meal_takeaway"]
leisure=["amusement_park","bowling_alley","casino","movie_rental","movie_theater","spa","stadium","zoo"]
culture=["art_gallery","library","museum","church","city_hall","synagogue","mosque","hindu_temple"]
services=["campground","car_rental","atm","parking","gas_station","police","rv_park"]
shopping=["book_store","clothing_store","convenience_store","department_store","electronics_store","hardware_store","florist","jewelry_store","pet_store","shopping_mall","store","supermarket"]
medical_services=["doctor","hospital","pharmacy"]
bar_and_clubs=["bar","cafe","night_club"]
transport=["airport","bus_station","train_station","subway_station","taxi_stand"]
other=["park"]

CATEGORIES = {'food':food,'leisure':leisure,'culture':culture,'services':services,'shopping':shopping,'medical_services':medical_services,'bar_and_clubs':bar_and_clubs,'transport':transport,'other':other}

#------------------------------------------------------------------------------------#
# Vista de alta de usuario. Crea una entidad User tanto en la aplicación como en     #
# el servicio web. Se crea también en la aplicación para poder acceder a propiedades #
# del usuario sin consultar el servicio web, como user.username; o hacer uso de la   #
# sentencia user.is_authenticaded                                                    #
#------------------------------------------------------------------------------------#

class SignUp(View):
    form_class = SignupForm
    template_name_on_success = 'venues/wireframe-index.html'
    template_name_on_login_error = 'registration/wireframe-login.html'
    template_name_on_signup_error = 'registration/wireframe-signup.html'
    template_name = 'registration/wireframe-signup.html'

    def get(self, request):
        return render(request, self.template_name, {'form':self.form_class})
    

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            data = {'username':username,'password':raw_password}
            print("About to create user: \n")
            print(data)
            signup_url = "http://127.0.0.1:8000/users/signup/"
            response = requests.post(signup_url, data)
            print(response.json())
            if response.ok:
                login_url = "http://127.0.0.1:8000/users/login/"
                response = requests.post(login_url, data = {'username':username,'password':raw_password})
                if response.ok:
                    token = response.json()['token']
                    request.session['auth_token'] = token
                    context = {}
                    return render(request, self.template_name_on_success, context)
                else:
                    messages.error(request,'Algo salió mal durante el inicio de sesión. Inténtalo más tarde.')
                    context = {'form':AuthenticationForm}
                    return render(request, self.template_name_on_login_error, context)
            else:
                messages.error(request,'Algo salió mal al intentar crear tu cuenta. Inténtalo más tarde.')
                context = {'form':self.form_class}
                return render(request, self.template_name_on_signup_error, context)
        else:
            return render(request, self.template_name_on_signup_error, {'form':form})
                
           
#------------------------------------------------------------------------------------#
# Vista de incio de sesión. Inicia sesión para un usuario tanto en la aplicación     #
# como en el servicio web. Se crea también en la aplicación para poder acceder a     #
# propiedades del usuario sin consultar el servicio web, como user.username; o hacer #
# uso de la sentencia user.is_authenticaded                                          #
#------------------------------------------------------------------------------------#


class Login(View):
    form_class = AuthenticationForm
    template_name_on_success = 'venues/wireframe-index.html'
    template_name_on_error = 'registration/wireframe-login.html'
    template_name = 'registration/wireframe-login.html'

    def get(self, request):
        return render(request, self.template_name, {'form':self.form_class})
    
    def post(self, request):
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            api_auth_url = 'http://127.0.0.1:8000/users/login/'
            response = requests.post(api_auth_url, data={'username':username, 'password':password})
            if response.ok:
                token = response.json()['token']
                request.session['auth_token'] = token
                context = {}
                return render(request, self.template_name_on_success, context)
            else:
                messages.error(request,'Algo salió mal al intentar iniciar tu sesión. Inténtalo más tarde.')
                context = {'form':self.form_class}
                return render(request, self.template_name_on_error, context)
        else:
            messages.error(request,'Usuario o contraseña incorrectos')
            context = {'form':self.form_class}
            return render(request, self.template_name_on_error, context)
        


#--------------------------------------------------------------------------------------#
# Vista índice. Redirige a la plantilla index.html, que presenta un formulario para la #
# búsqueda de puntos de interés. Esta plantilla solicitará permiso del usuario para    #
# obtener su localización                                                              #
#--------------------------------------------------------------------------------------#

class Index(View):
    template_name = 'venues/wireframe-index.html'
    
    def get(self, request):
        context = {}
        return render(request, self.template_name, context)

#Comprueba si los detalles del lugar existen en la caché, si no los solicita al servicio web
def tryCachedDetails(place_id):

    details = ""
    if place_id in PLACE_DETAIL_CACHE:
                details = PLACE_DETAIL_CACHE[place_id]
    else:
        url="http://127.0.0.1:8000/external-api/getvenues/"+place_id
        response = requests.get(url)
        if response.ok:
            details = json.loads(response.content.decode('utf-8'))
        else:#No se pudieron obtener los detalles (No debería pasar nunca)-Personalizar el mensaje de error según el código de respuesta
            error_msg = str(response.status_code)+":"+response.reason
            messages.error(request,error_msg)
            context = {}
            return render(request, self.template_name_on_error, context)
    return details

def prepareComments(comments, user):

    comment_list = []
    if comments:
        for element in comments:
            item = {}
            item['date'] = parser.parse(element['created']).strftime('%m/%d/%Y - %H:%M:%S')
            item['text'] = element['text']
            item['owner'] = element['owner']
            item['id'] = element['id']
            if element['owner'] == str(user):
                item['editable'] = True
            if element['image']:
                item['image'] = element['image']
            comment_list.append(item)
 
    return comment_list 

def getPageNumber(string):

    start = string.find("page=")
    if start!=-1:
        end = start + len("page=") + 2
        substr = string[start:end]
        if '&' not in substr[-2:]:
            return substr[-2:]
        else:
            return substr[-2:-1]
    else:
        return None
#-------------------------------------------------------------------------------------------#
# Vista para postear nuevos comentarios. Almacena el comentario en el servicio web mediante #
# una petición POST, y a continuación recupera la lista actualizada de comentarios y fotos. #
# Existe por lo menos un comentario nuevo que debe ser mostrado (el enviado), pero en ese   #
# tiempo otros usuarios podrían haber enviado nuevos comentarios o fotos.                   #
#-------------------------------------------------------------------------------------------#


class PostNewComment(View):
    template_name = 'venues/wireframe-detail.html'
    template_name_on_error = 'venues/error.html'

    def post(self, request, place_id):
        next = ""
        previous = ""
        image_list = []
        comment_list = []
        comment = request.POST["text"];
        rating = request.POST["rating"]
        image = None
        if "image" in request.FILES:
            stream = request.FILES["image"].file
            image = base64.b64encode(stream.getvalue())
        
        url = "http://127.0.0.1:8000/comments/"

        response = requests.post(url, data = {'text':comment, 'rating':rating, 'image':image, 'venue_id': place_id}, headers = {'Authorization':'token '+request.session['auth_token']}) 
        if response.ok:
            r = requests.get(url+"?venue_id="+place_id)
            if r.ok:
                data = json.loads(r.content.decode('utf-8'))
                comments = data['results']
                if 'next' in data and data['next'] is not None:
                    page = getPageNumber(data['next'])
                    if page:
                        next = page
                if 'previous' in data and data['previous'] is not None:
                    if content_page == "2":
                        previous = "0"
                    else: 
                        page = getPageNumber(data['previous'])
                        if page:
                            previous = page
            else:
                comments = ""
                messages.error(request,"No se pudieron recuperar los comentarios")

            comment_list = prepareComments(comments, self.request.user)
                    
            details = tryCachedDetails(place_id)
            phone_number = ""
            address = ""
            website = ""
            schedule = ""
            categories = ""        
            name = details['result']['name']
            if 'formatted_phone_number' in details['result']: 
                phone_number = details['result']['formatted_phone_number']
            if 'formatted_address' in details['result']:
                address = details['result']['formatted_address']
            if 'website' in details['result']:
                website = details['result']['website']
            if 'opening_hours' in details['result'] and 'weekday_text' in details['result']['opening_hours']:
                schedule = details['result']['opening_hours']['weekday_text']
            if 'types' in details['result']:
                categories = details['result']['types']
            context = {"comments":comment_list, 'name':name, 'phone_number':phone_number, 'address':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id, 'next':next, 'previous':previous}
            return render(request, self.template_name, context)
        else: #No se pudo añadir el comentario
            messages.error(request,"Debido a un error, no se ha podido añadir tu comentario. Inténtalo más tarde.")
            context = {}
            return render(request, self.template_name, context)

class DeleteComment(View):
    template_name = 'venues/wireframe-detail.html'

    def get(self, request, place_id, comment_id):
        next = ""
        previous = ""

        url = "http://127.0.0.1:8000/comments/"

        requests.delete(url+comment_id, headers = {'Authorization':'token '+request.session['auth_token']})
   
        response = requests.get(url+"?venue_id="+place_id)
        if response.ok:
            data = json.loads(r.content.decode('utf-8'))
            comments = data['results']
            if 'next' in data and data['next'] is not None:
                page = getPageNumber(data['next'])
                if page:
                    next = page
            if 'previous' in data and data['previous'] is not None:
                if content_page == "2":
                    previous="0"
                else: 
                    page = getPageNumber(data['previous'])
                    if page:
                        previous = page
        else:
            comments = ""
            messages.error(request,"No se pudieron recuperar los comentarios")

        comment_list = prepareComments(comments, self.request.user)
                    
        details = tryCachedDetails(place_id)
        phone_number = ""
        address = ""
        website = ""
        schedule = ""
        categories = ""        
        name = details['result']['name']
        if 'formatted_phone_number' in details['result']: 
            phone_number = details['result']['formatted_phone_number']
        if 'formatted_address' in details['result']:
            address = details['result']['formatted_address']
        if 'website' in details['result']:
            website = details['result']['website']
        if 'opening_hours' in details['result'] and 'weekday_text' in details['result']['opening_hours']:
            schedule = details['result']['opening_hours']['weekday_text']
        if 'types' in details['result']:
            categories = details['result']['types']
        context = {"comments":comment_list, 'name':name, 'phone_number':phone_number, 'address':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id, 'next':next, 'previous':previous}
        return render(request, self.template_name, context)


        


#---------------------------------------------------------------------------------------------#
# Vista detalle. Obtiene y presenta los detalles de un punto de interés a través del servicio #
# web, junto con las fotos y comentarios asociados a este                                     #
#---------------------------------------------------------------------------------------------#

class Detail(View):
    template_name = 'venues/wireframe-detail-jquery.html'
    template_name_on_error = 'venues/error.html'

    def get(self, request, place_id, content_page=''):
        image_list = []
        comment_list = []
        next = ""
        previous = ""
        url="http://127.0.0.1:8000/external-api/getvenues/"+place_id
        response = requests.get(url)

        #Retrieve venue details
        if response.ok:
            jData = json.loads(response.content.decode('utf-8'))
            
            phone_number = ""
            address = ""
            website = ""
            schedule = ""
            categories = ""
 
            name = jData['result']['name']
            if 'formatted_phone_number' in jData['result']: 
                phone_number = jData['result']['formatted_phone_number']
            if 'formatted_address' in jData['result']:
                address = jData['result']['formatted_address']
            else:
                #address = geocode(jData['result']['geometry']['location']['lat'],lng)
                response = requests.get("http://127.0.0.1:8000/external-api/reverse-geocode/?LatLng="+jData['result']['geometry']['location']['lat']+","+jData['result']['geometry']['location']['lng'])
                if response.ok:
                    data=response.json();
                    for component in data['results'][0]['address_components']:
                        if 'street_number' in component['types']:
                            street_number = component['long_name']
                        if 'route' in component['types']:
                            route = component['long_name']
                        if 'locality' in component['types']:
                            locality = component['long_name']
                        if 'administrative_area_level_2' in component['types']:
                            administrative_area_level_2 = component['long_name']
                        if 'administrative_area_level_1' in component['types']:
                            administrative_area_level_1 = component['long_name']
                        if 'country' in component['types']:
                            country = component['long_name']
                        if 'postal_code' in component['types']:
                            postal_code = component['long_name']
                    address = route+", Nº:"+street_number+", CP:"+postal_code+", "+locality+", "+administrative_area_level_2+", "+administrative_area_level_1+", "+country
            if 'website' in jData['result']:
                website = jData['result']['website']
            if 'opening_hours' in jData['result'] and 'weekday_text' in jData['result']['opening_hours']:
                schedule = jData['result']['opening_hours']['weekday_text']
            if 'types' in jData['result']:
                categories = jData['result']['types']

            context = {'name':name, 'phone_number':phone_number, 'address':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id}
            return render(request, self.template_name, context)
        else: #Personalizar el mensaje de error según el código de respuesta
            error_msg = str(response.status_code)+":"+response.reason
            messages.error(request,error_msg)
            context = {}
            return render(request, self.template_name_on_error, context)

def cacheInSession(jData, request):
    
    for item in jData['results']:
        for category in CATEGORIES:
            if any(t in CATEGORIES[category] for t in item['types']):
                exists = False
                if request.session[category]:
                    for element in request.session[category]:
                        if element['id'] == item['id']:
                            exists = True
                            break
                    if not exists:
                        request.session[category].append(item)
                else:
                    request.session[category].append(item) 


#Función auxiliar para limpiar caracteres conflictivos de la respuesta y aplicar filtrado.
def cleanResponse(jData): 

            required_keys = ["venue_name", "lat", "venue_id", "rating", "reference", "category", "icon", "lng"]

            
            #request.session[jData['results']['category']] = jData
            df = pd.DataFrame(jData)[required_keys] 
            #----------------Filtrado----------------------------------
            #df['types'] = df['types'].apply(lambda x: any(e in CATEGORIES[category] for e in x))
            #df = df.loc[df['types'] == True]
            #----------------Filtrado----------------------------------
            #Limpieza de caracteres conflictivos
            df["venue_name"] = df["venue_name"].apply(lambda x: x.replace("'",""))
            df["venue_name"] = df["venue_name"].apply(lambda x: x.replace("`",""))
            df = df.fillna(0) #Cambia los valores NaN por 0
            #Filtrado de valores booleanos para sustituirlos por String-----------------------
            #mask = df.applymap(type) != bool
            #replacement_dict = {True: 'Abierto', False: 'Cerrado'}
            #df = df.where(mask, df.replace(replacement_dict))
            #---------------------------------------------------------------------------------
            d = df.to_json(orient='records')
            return d

def formatCategory(category):
    finalString = ""
    for element in category:
        finalString+=element+"|"
    return finalString[:-1]

#-------------------------------------------------------------------------------------------#
# Vista de mapa. Procesa los resultados de puntos de interés obtenidos del servicio web y   # 
# realiza las preparaciones pertinentes (como eliminar caracteres extraños que puedan       #
# provocar un error al parsear el texto JSON dentro del código JavaScript de la plantilla   #
# mapview.html)                                                                             #
#-------------------------------------------------------------------------------------------#

class Mapview(View):
    template_name = 'venues/mapview.html'
    template_name_on_error = 'venues/error.html'

    def post(self, request):
        position = request.POST['position']
        radius = request.POST['radius']
        request.session['radius'] = radius
        category = request.POST['category']
        
        if position:
            user_coordinates = {'lat': float(position.split(",")[0]), 'long': float(position.split(",")[1])}
            request.session['user_coordinates'] = user_coordinates
            print(user_coordinates)
            url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s&category=%s" % (user_coordinates['lat'],user_coordinates['long'],radius, category) #url vieja con campo categoría
            #url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s" % (user_coordinates['lat'],user_coordinates['long'],radius)
            print(url)
            response = requests.get(url)
        else:
            messages.error(request,"Error al tratar de obtener tu ubicación.")
            context = {}
            return render(request, self.template_name, context)

        if response.ok:
            #jData = json.loads(response.content.decode('utf-8'))
            jData = response.json()
            #cacheInSession(jData, request)
            d = cleanResponse(jData)
            venues = json.loads(d)
            user_coordinates_json = json.loads(json.dumps(user_coordinates))
            rating_url = "http://127.0.0.1:8000/ratings/"
            r = requests.get(rating_url)
            if r.ok:
                ratings = r.json()
                aux_dict = {}
                for rating in ratings['results']:
                    aux_dict[rating['venue_id']] = rating['avg_rating']
                for venue in venues:
                    if venue['reference'] in aux_dict:
                        venue['rating'] = aux_dict[venue['reference']]
                    else:
                        venue['rating'] = "0.00"
            context = {'venues':venues, 'user_location': user_coordinates_json, 'initial_category':category}
            return render(request, self.template_name, context)
        else: #Personalizar el mensaje de error según el código de respuesta
            error_msg = str(response.status_code)+":"+response.reason
            messages.error(request,"Error al tratar de obtener puntos de interés cerca de tu ubicación.")
            context = {}
            return render(request, self.template_name, context)

class GetAvgRating(View):

    def get(self, request):
        place_id = request.GET['venue_id']
        url = "http://127.0.0.1:8000/ratings/?venue_id="+place_id
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(500)

class NewComment(View):

    def post(self, request):
        place_id = request.GET['venue_id']
        print("place_id:"+place_id)
        comment = request.POST["text"]
        rating = request.POST["rating"]
        print("rating:"+rating)
        image = None
        if "image" in request.FILES:
            stream = request.FILES["image"].file
            image = base64.b64encode(stream.getvalue())
        
        url = "http://127.0.0.1:8000/comments/"
        response = requests.post(url, data = {'text':comment, 'rating':rating, 'venue_id': place_id}, headers = {'Authorization':'token '+request.session['auth_token']}) # se ha quitado 'image':image de data, ahora las fotos van separadas
        print(response.json())
        if response.ok:
            return HttpResponse(201)
        else:
            return HttpResponse(500)

class GetComments(View):

    def get(self, request):
        place_id = request.GET['venue_id']
        page = request.GET['page']
        comments_url = "http://127.0.0.1:8000/comments/?venue_id="+place_id
        if page and page!="1":
            comments_url = "http://127.0.0.1:8000/comments/?page="+page+"&venue_id="+place_id

        r = requests.get(comments_url)
        if r.ok:
            data = r.json()
            print(data)
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(500)

class RemoveComment(View):

    def get(self, request):
        comment_id = request.GET['comment_id']

        comments_url = "http://127.0.0.1:8000/comments/"
        response = requests.delete(comments_url+comment_id, headers = {'Authorization':'token '+request.session['auth_token']})

        if response.ok:
            return HttpResponse(204)
        else:
            return HttpResponse(500)

#-------------------------------------------------------------------------------------------#
# Vista de filtros por categoría. Vuelve a cargar la respuesta original del servicio en un  #
# DataFrame y aplica el filtrado correspondiente. Vista invocada por llamada AJAX mediante  #   
# jQuery                                                                                    #
#-------------------------------------------------------------------------------------------#

class Filter(View):

    def get(self, request):
        categories = request.GET['category'].split("|")
        user_coordinates = request.session['user_coordinates']
        radius = request.session['radius']
        formattedCategories = ",".join(categories)
     
        #for category in categories:
        #    if request.session[category]:
        #        print("Existe en caché la categoría: "+category)
        #        content.extend(request.session[category])
        #    else:
        #        print("No existe en caché la categoría: "+category)
        #        formattedCategories += formatCategory(CATEGORIES[category])
        #        print("Se añade a la petición. Estado actual: "+formattedCategories)

        #if content:
        #    print("Se prepara el contenido de la caché")
        #    content = cleanResponse(content)
        #    finalResult.extend(content)

        url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s&category=%s" % (user_coordinates['lat'],user_coordinates['long'],radius, formattedCategories)
        response = requests.get(url)

        if response.ok:
            print("Se prepara el nuevo contenido recuperado")
            jData = response.json()
            d = cleanResponse(jData)
            return HttpResponse(d, content_type="application/json")
        #else if zero_results devolver un codigo de error que salte un mensaje no hay resultados en el mapa
        #else devolver un codigo que haga saltar lo de ha habido un error, intentalo mas tarde
            
        #if finalResult:
        #    return HttpResponse(finalResult, content_type="application/json")
            # o json.dumps(jData)
        else:
            return HttpResponse(500)
     

        



