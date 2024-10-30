from django.urls import include, path
from . import views

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('profile/<str:username>', views.UserProfile.as_view(), name='profile'),
    path('registration/', views.UserCreateView.as_view(), name='registration')
]
