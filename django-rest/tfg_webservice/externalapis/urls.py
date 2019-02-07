from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from externalapis import views

urlpatterns = [
    url(r'^external-api/getvenues/$', views.ExternalAPI_getvenues_async.as_view()), 
    url(r'^external-api/reverse-geocode/$', views.ExternalAPI_getaddress.as_view()), 
    url(r'^external-api/getvenues/(?P<place_id>[\w\-]+)$', views.ExternalAPI_getplacedetail.as_view()), 
]

urlpatterns = format_suffix_patterns(urlpatterns)
