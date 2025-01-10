from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('v2/posts', views.PostViewSet)
router.register('v2/categories', views.CategoryViewSet)
router.register(
    r'v2/posts/(?P<post_id>[\d]+)/comments(?P<comment_id>[\d]*)',
    views.CommentVeiwSet,
    basename='Comment'
)

urlpatterns = [
    path('', include(router.urls)),
]
