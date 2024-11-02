from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.PostCreate.as_view(), name='post_create'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('posts/<int:pk>/edit/', views.PostUpdate.as_view(), name='post_edit'),
    path(
        'posts/<int:pk>/delete/',
        views.PostDelete.as_view(),
        name='post_delete'
    ),
    path(
        'posts/<int:pk>/comment/',
        views.CommentCreate.as_view(),
        name='comment_create'
    ),
    path(
        'posts/<int:post_pk>/edit/<int:pk>/',
        views.CommentUpdate.as_view(),
        name='comment_edit'
    ),
    path(
        'posts/<int:post_pk>/delete_comment/<int:pk>/',
        views.CommentDelete.as_view(),
        name='comment_delete'
    ),
    ]
