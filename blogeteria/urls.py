from django.contrib import admin
from django.conf import settings
from django.urls import include, path

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.forbidden'
handler500 = 'core.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('users.urls', namespace='users'))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
