from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    context = {}
    return render(request, 'venues/index.html', context)

def mapview(request):
    travel_mode = request.POST['travel_mode']
    radius = request.POST['radius']
    category = request.POST['category']
    context = {'travel_mode':travel_mode, 'radius':radius, 'category':category}
    return render(request, 'venues/mapview.html', context)


