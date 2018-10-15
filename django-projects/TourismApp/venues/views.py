import requests
import json
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


class Mapview(View):
    template_name = 'venues/mapview.html'

    def post(self, request):
        travel_mode = request.POST['travel_mode']
        radius = request.POST['radius']
        category = request.POST['category']

        user_coordinates = {'lat': "43.3712591", 'long': "-8.4188010"}

        url="http://127.0.0.1:8000/external-api/getvenues/?LatLng=%s,%s&radius=%s" % (user_coordinates['lat'],user_coordinates['long'],radius)
        response = requests.get(url)

        if response.ok:
            jData = json.loads(response.content.decode('utf-8'))
            venue_dict = {}
            dict_entry = {}
            for venue in jData['results']:
                name = venue['name']
                dict_entry = {'lat': venue['geometry']['location']['lat'], 'long': venue['geometry']['location']['lng']}
                venue_dict[name] = dict_entry
            r = json.dumps(venue_dict)
            loaded_r = json.loads(r)
            context = {'venues':venue_dict, 'venues_json':loaded_r, 'dump':r}
            return render(request, self.template_name, context)
        else:
            error_msg = str(response.status_code)+":"+response.reason
            raise Exception(error_msg)

        #context = {'travel_mode':travel_mode, 'radius':radius, 'category':category, 'request':request}
        #return render(request, self.template_name, context)




