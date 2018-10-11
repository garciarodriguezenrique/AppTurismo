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
        context = {'travel_mode':travel_mode, 'radius':radius, 'category':category, 'request':request}
        return render(request, self.template_name, context)




