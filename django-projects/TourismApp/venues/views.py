import requests
import json
import geocoder
import base64
import pandas as pd
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
food="restaurant|meal_delivery|meal_takeaway"
leisure="amusement_park|bowling_alley|casino|movie_rental|movie_theater|spa|stadium|zoo"
culture="art_gallery|library|museum|church|city_hall|synagogue|mosque|hindu_temple"
services="campground|car_rental|atm|parking|gas_station|police|rv_park"
shopping="book_store|clothing_store|convenience_store|department_store|electronics_store|hardware_store|florist|jewelry_store|pet_store|shopping_mall|store|supermarket"
medical_services="doctor|hospital|pharmacy"
bar_and_clubs="bar|cafe|night_club"
transport="airport|bus_station|train_station|subway_station|taxi_stand"
other="park"

CATEGORIES = {'food':food,'leisure':leisure,'culture':culture,'services':services,'shopping':shopping,'medical_services':medical_services,'bar_and_clubs':bar_and_clubs,'transport':transport,'other':other}

#------------------------------------------------------------------------------------#
# Vista de alta de usuario. Crea una entidad User tanto en la aplicación como en     #
# el servicio web. Se crea también en la aplicación para poder acceder a propiedades #
# del usuario sin consultar el servicio web, como user.username; o hacer uso de la   #
# sentencia user.is_authenticaded                                                    #
#------------------------------------------------------------------------------------#

class SignUp(View):
    form_class = SignupForm
    template_name_on_success = 'venues/index.html'
    template_name_on_login_error = 'registration/login.html'
    template_name_on_signup_error = 'registration/signup.html'

    def get(self, request):
        return render(request, self.template_name_on_signup_error, {'form':self.form_class})
    

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            data = {'username':username,'password':raw_password}
            signup_url = "http://127.0.0.1:8000/users/signup/"
            response = requests.post(signup_url, data)
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
                messages.error(request,'Algo salió mal durante al intentar crear tu cuenta. Inténtalo más tarde.')
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
    template_name_on_success = 'venues/index.html'
    template_name_on_error = 'registration/login.html'
    
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
    template_name = 'venues/index.html'
    
    def get(self, request):
        context = {}
        return render(request, self.template_name, context)

#-------------------------------------------------------------------------------------------#
# Vista para postear nuevos comentarios. Almacena el comentario en el servicio web mediante #
# una petición POST, y a continuación recupera la lista actualizada de comentarios y fotos. #
# Existe por lo menos un comentario nuevo que debe ser mostrado (el enviado), pero en ese   #
# tiempo otros usuarios podrían haber enviado nuevos comentarios o fotos.                   #
#-------------------------------------------------------------------------------------------#


class PostNewComment(View):
    template_name = 'venues/detail.html'
    template_name_on_error = 'venues/error.html'

    def post(self, request, place_id):
        image_list = []
        comment = request.POST["text"];
        
        url = "http://127.0.0.1:8000/comments/"

        response = requests.post(url, data = {'text':comment, 'venue_id': place_id}, headers = {'Authorization':'token '+request.session['auth_token']}) 
        if response.ok:
            r = requests.get(url+"?venue_id="+place_id)
            if r.ok:
                comments = json.loads(r.content.decode('utf-8'))['results']
            else:
                comments = ""
                messages.error(request,"No se pudieron recuperar los comentarios")
            images_url = "http://127.0.0.1:8000/images/?venue_id="+place_id
            r = requests.get(images_url)
            if r.ok:
                images = json.loads(r.content.decode('utf-8'))['results']
            else:
                images = ""
                messages.error(request,"No se pudieron recuperar las imágenes")
            if images:
                for element in images:
                    image_list.append(element['image'])
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
                    
                    
            name = details['result']['name']
            phone_number = details['result']['formatted_phone_number']
            address = details['result']['formatted_address']
            website = details['result']['website']
            schedule = details['result']['opening_hours']['weekday_text']
            categories = details['result']['types']
            context = {"comments":comments, 'images':image_list, 'name':name, 'phone_number':phone_number, 'addess':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id}
            return render(request, self.template_name, context)
        else: #No se pudo añadir el comentario
            messages.error(request,"Debido a un error, no se ha podido añadir tu comentario. Inténtalo más tarde.")
            context = {}
            return render(request, self.template_name, context)
        
#-------------------------------------------------------------------------------------------#
# Vista para postear nuevas fotografías. Almacena la fotografía en el servicio web mediante #
# una petición POST, y a continuación recupera la lista actualizada de comentarios y fotos. #
# Existe por lo menos una imagen nueva que debe ser mostrada (la enviada), pero en ese      #
# tiempo otros usuarios podrían haber enviado nuevos comentarios o fotos.                   #
#-------------------------------------------------------------------------------------------#


class PostNewImage(View):
    template_name = 'venues/detail.html'
    template_name_on_error = 'venues/error.html'

    def post(self, request, place_id):
        image_list = []
        stream = request.FILES["image"].file
        image = base64.b64encode(stream.getvalue())
        caption = request.POST["caption"]
        
        url = "http://127.0.0.1:8000/images/"
        
        response = requests.post(url, data = {'image':image, 'caption':caption, 'venue_id': place_id}, headers = {'Authorization':'token '+request.session['auth_token']}) 
        if response.ok:
            r = requests.get(url+"?venue_id="+place_id)
            if r.ok:
                images = json.loads(r.content.decode('utf-8'))['results']
            else:
                images = ""
                messages.error(request,"No se pudieron recuperar las imágenes")
            if images:
                for element in images:
                    image_list.append(element['image'])
            comments_url = "http://127.0.0.1:8000/comments/?venue_id="+place_id
            r = requests.get(comments_url)
            if r.ok:
                comments = json.loads(r.content.decode('utf-8'))['results']
            else:
                comments = ""
                messages.error(request,"No se pudieron recuperar los comentarios") 
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
            name = details['result']['name']
            phone_number = details['result']['formatted_phone_number']
            address = details['result']['formatted_address']
            website = details['result']['website']
            schedule = details['result']['opening_hours']['weekday_text']
            categories = details['result']['types']
            context = {'comments':comments, 'images':image_list, 'name':name, 'phone_number':phone_number, 'addess':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id}
            return render(request, self.template_name, context)
        else: #No se pudo añadir la imagen
            messages.error(request,"Debido a un error, no se ha podido añadir tu foto. Inténtalo más tarde.")
            context = {}
            return render(request, self.template_name, context)

#---------------------------------------------------------------------------------------------#
# Vista detalle. Obtiene y presenta los detalles de un punto de interés a través del servicio #
# web, junto con las fotos y comentarios asociados a este                                     #
#---------------------------------------------------------------------------------------------#

class Detail(View):
    template_name = 'venues/detail.html'
    template_name_on_error = 'venues/error.html'

    def get(self, request, place_id):
        image_list = []
        url="http://127.0.0.1:8000/external-api/getvenues/"+place_id
        response = requests.get(url)

        #Retrieve venue details
        if response.ok:
            jData = json.loads(response.content.decode('utf-8'))
            #Retrieve user comments
            comments_url = "http://127.0.0.1:8000/comments/?venue_id="+place_id
            r = requests.get(comments_url)
            if r.ok:
                comments = json.loads(r.content.decode('utf-8'))['results']
            else:
                comments = ""
                messages.error(request,"No se pudieron recuperar las imágenes")
            #Retrieve user images
            images_url = "http://127.0.0.1:8000/images/?venue_id="+place_id
            r = requests.get(images_url)
            if r.ok:
                images = json.loads(r.content.decode('utf-8'))['results']
            else:
                images = ""
                messages.error(request,"No se pudieron recuperar las imágenes")
            if images:
                for element in images:
                    image_list.append(element['image'])
            PLACE_DETAIL_CACHE[place_id] = jData 
            name = jData['result']['name']
            phone_number = jData['result']['formatted_phone_number']
            address = jData['result']['formatted_address']
            website = jData['result']['website']
            schedule = jData['result']['opening_hours']['weekday_text']
            categories = jData['result']['types']
            context = {'name':name, 'phone_number':phone_number, 'addess':address, 'website':website, 'schedule':schedule, 'categories':categories, 'id': place_id, 'comments':comments, 'images':image_list}
            return render(request, self.template_name, context)
        else: #Personalizar el mensaje de error según el código de respuesta
            error_msg = str(response.status_code)+":"+response.reason
            messages.error(request,error_msg)
            context = {}
            return render(request, self.template_name_on_error, context)


#Actualmente en desuso dados los problemas para parsear con jQuery el resultado de df.to_json()
def cleanResponse(df): 

    #Limpieza de caracteres conflictivos
            df["name"] = df["name"].apply(lambda x: x.replace("'",""))
            df['opening_hours'] = df['opening_hours'].apply(pd.Series)['open_now'] #Extrae el valor de la clave anidada 'open_now'. Posiblemente se quite de aquí y sea algo que se encargue de mostrar la vista detalle, porque es problematico parsearlo con JS en el caso de la respuesta filtrada.
            df = df.fillna(0) #Cambia los valores NaN por 0
            #Filtrado de valores booleanos para sustituirlos por String-----------------------
            mask = df.applymap(type) != bool
            replacement_dict = {True: 'Abierto', False: 'Cerrado'}
            df = df.where(mask, df.replace(replacement_dict))
            #---------------------------------------------------------------------------------
            d = df.to_json(orient='records')
            return d

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
        travel_mode = request.POST['travel_mode']
        position = request.POST['position']
        radius = request.POST['radius']
        request.session['radius'] = radius
        category = request.POST['category']
        
        if position:
            user_coordinates = {'lat': float(position.split(",")[0]), 'long': float(position.split(",")[1])}
            request.session['user_coordinates'] = user_coordinates
            print(user_coordinates)
            #url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s&category=%s" % (user_coordinates['lat'],user_coordinates['long'],radius, CATEGORIES[category]) url vieja con campo categoría
            url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s" % (user_coordinates['lat'],user_coordinates['long'],radius)
            print(url)
            response = requests.get(url)
        else:
            messages.error(request,"Error al tratar de obtener tu ubicación.")
            context = {}
            return render(request, self.template_name, context)

        if response.ok:
            print("Response is ok")
            jData = json.loads(response.content.decode('utf-8'))
            request.session['initial-response'] = jData['results'] #Almacenado en la sesión para después poder filtrar.
            #Campos de la respuesta que queremos integrar en el DataFrame
            required_keys = ["name", "geometry", "id", "opening_hours", "price_level", "rating", "types"]
            df = pd.DataFrame(jData['results'])[required_keys]
            #----------------Filtrado----------------------------------
            df['types'] = df['types'].apply(lambda x: any(e in CATEGORIES[category] for e in x))
            df = df.loc[df['types'] == True]
            #----------------Filtrado----------------------------------
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
        else: #Personalizar el mensaje de error según el código de respuesta
            error_msg = str(response.status_code)+":"+response.reason
            messages.error(request,"Error al tratar de obtener puntos de interés cerca de tu ubicación.")
            context = {}
            return render(request, self.template_name, context)

#-------------------------------------------------------------------------------------------#
# Vista de filtros por categoría. Vuelve a cargar la respuesta original del servicio en un  #
# DataFrame y aplica el filtrado correspondiente. Vista invocada por llamada AJAX mediante  #   
# jQuery                                                                                    #
#-------------------------------------------------------------------------------------------#

class Filter(View):

    def get(self, request):
        category = request.GET['category']
        #url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s&category=%s" % (user_coordinates['lat'],user_coordinates['long'],radius, CATEGORIES[category]) url vieja con campo categoría
        #url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s" % (request.session['user_coordinates']['lat'],request.session['user_coordinates']['long'],request.session['radius'])
        #response = requests.get(url)
        #if response.ok:
        #    data = response.json()
        #else:
        #    return HttpResponse(500)

        jData = request.session["initial-response"]
        required_keys = ["name", "geometry", "id", "opening_hours", "price_level", "rating", "types"]
        df = pd.DataFrame(jData)[required_keys]
        #----------------Filtrado----------------------------------
        df['types'] = df['types'].apply(lambda x: any(e in CATEGORIES[category] for e in x))
        df = df.loc[df['types'] == True]
        #----------------Filtrado----------------------------------
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
        #---------------------------------------------------
        return HttpResponse(json.dumps(json.loads(d)), content_type="application/json")


        



