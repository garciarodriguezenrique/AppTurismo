from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from .forms import SignupForm


class SignUp(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

def index(request):
    context = {}
    return render(request, 'venues/index.html', context)

def mapview(request):
    travel_mode = request.POST['travel_mode']
    radius = request.POST['radius']
    category = request.POST['category']
    context = {'travel_mode':travel_mode, 'radius':radius, 'category':category, 'request':request}
    return render(request, 'venues/mapview.html', context)


