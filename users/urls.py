from django.urls import include, path
from . import views

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path(
        'profile/<str:username>/', views.user_profile_view, name='profile'),
    path('registration/', views.UserCreateView.as_view(), name='registration'),
    path(
        'profile/<int:pk>/edit/',
        views.UserChangeView.as_view(),
        name='profile_edit')
]
