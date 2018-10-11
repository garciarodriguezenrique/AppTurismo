from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from externalapis import views

urlpatterns = [
    url(r'^external-api/$', views.ExternalAPI.as_view()), 
    url(r'^external-api/getmap/$', views.ExternalAPI_getmap.as_view()), 
]

urlpatterns = format_suffix_patterns(urlpatterns)
