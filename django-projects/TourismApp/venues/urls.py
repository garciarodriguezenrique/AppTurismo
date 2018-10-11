from django.urls import path

from . import views


app_name = 'venues'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('show-results/', views.Mapview.as_view(), name='mapview'),
    path('signup/', views.SignUp.as_view(), name='signup')
]
