from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from usercontent import views

urlpatterns = [
    url(r'^comments/$', views.CommentList.as_view()),
    url(r'^comments/(?P<pk>[0-9]+)/$', views.CommentDetail.as_view()),
    url(r'^images/$', views.ImageList.as_view()),
    url(r'^images/(?P<pk>[0-9]+)/$', views.ImageDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()), 
]

urlpatterns = format_suffix_patterns(urlpatterns)
