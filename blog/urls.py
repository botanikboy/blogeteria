from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.PostCreate.as_view(), name='post_create'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('posts/<int:pk>/edit/', views.PostUpdate.as_view(), name='post_edit'),
]
