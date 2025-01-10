from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('v2/posts', views.PostViewSet)

urlpatterns = [
    path('v1/posts/', views.APIPostList.as_view()),
    path('v1/posts/<int:pk>/', views.APIPostDetail.as_view()),
    path('', include(router.urls)),
]
