from django.urls import path, re_path

from . import views


app_name = 'venues'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('show-results/', views.Mapview.as_view(), name='mapview'),
    re_path('get_location_string/$', views.ReverseGeocode.as_view(), name='reverse-geocode'),
    re_path('filter-results/$', views.Filter.as_view(), name='filter'),
    re_path('get_comments/$', views.GetComments.as_view(), name='getcomments'),
    re_path('get_images/$', views.GetImages.as_view(), name='getimages'),
    re_path('get_avgrating/$', views.GetAvgRating.as_view(), name='getavgrating'),
    re_path('new_comment/$', views.NewComment.as_view(), name='newcomment'),
    re_path('remove_comment/$', views.RemoveComment.as_view(), name='removecomment'),
    re_path('new_image/$', views.NewImage.as_view(), name='newimage'),
    re_path('remove_image/$', views.RemoveImage.as_view(), name='removeimage'),
    path('show-results/<str:place_id>/', views.Detail.as_view(), name='detail'),
    path('show-results/<str:place_id>/<str:content_page>', views.Detail.as_view(), name='detail'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login')
]




