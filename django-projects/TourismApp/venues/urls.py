from django.urls import path

from . import views


app_name = 'venues'
urlpatterns = [
    path('', views.index, name='index'),
    path('show-results/', views.mapview, name='mapview')
]
