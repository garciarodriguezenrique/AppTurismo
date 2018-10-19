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

            url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s" % (user_coordinates['lat'],user_coordinates['long'],radius)
            response = requests.get(url)
        else:
            raise Exception("Geolocation data for your current position could not be retrieved.")

        if response.ok:
            jData = json.loads(response.content.decode('utf-8'))
            #Campos de la respuesta que queremos integrar en el DataFrame
            required_keys = ["name", "geometry"]
            df = pd.DataFrame(jData['results'])[required_keys]

            #Limpieza de caracteres conflictivos
            df["name"] = df["name"].apply(lambda x: x.replace("'",""))
            d = df.to_json(orient='records')
            venues = json.loads(d)
            user_coordinates_json = json.loads(json.dumps(user_coordinates))
            context = {'venues':venues, 'user_location': user_coordinates_json}
            return render(request, self.template_name, context)
        else:
            error_msg = str(response.status_code)+":"+response.reason
            raise Exception(error_msg)

#        if response.ok:
#            jData = json.loads(response.content.decode('utf-8'))
#            venue_dict = {}
#            dict_entry = {}
#            for venue in jData['results']:
#                name = venue['name']
#                if "'" in name:
#                    name = name.replace("'","")
#                dict_entry = {'lat': venue['geometry']['location']['lat'], 'long': venue['geometry']['location']['lng']}
#                venue_dict[name] = dict_entry
#            r = json.dumps(venue_dict)
#            loaded_r = json.loads(json.dumps(venue_dict))
#            user_coordinates_json = json.loads(json.dumps(user_coordinates))
#            context = {'venues':venue_dict, 'venues_json':loaded_r, 'user_location': user_coordinates_json}
#            return render(request, self.template_name, context)
#        else:
#            error_msg = str(response.status_code)+":"+response.reason
#            raise Exception(error_msg)

        #context = {'travel_mode':travel_mode, 'radius':radius, 'category':category, 'request':request}
        #return render(request, self.template_name, context)




