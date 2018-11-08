from django.urls import path, re_path

from . import views


app_name = 'venues'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('show-results/', views.Mapview.as_view(), name='mapview'),
    re_path('filter-results/$', views.Filter.as_view(), name='filter'),
    path('show-results/<str:place_id>/', views.Detail.as_view(), name='detail'),
    path('show-results/<str:place_id>/new_comment/', views.PostNewComment.as_view(), name='postnewcomment'),
    path('show-results/<str:place_id>/new_image/', views.PostNewImage.as_view(), name='postnewimage'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login')
]




