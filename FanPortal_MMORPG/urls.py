from ckeditor_uploader.views import upload, browse
from django.contrib.auth.decorators import login_required
from django.urls import re_path
from django.views.decorators.cache import never_cache
from django.views.static import serve
from django.conf import settings

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from adverts.views import page_not_found

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    path('admin/', admin.site.urls),
    path('', include('adverts.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('users/', include('users.urls', namespace="users")),

    re_path(r'^upload/', login_required(upload), name='ckeditor_upload'),
    re_path(r'^browse/', login_required(never_cache(browse)), name='ckeditor_browse'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = page_not_found
