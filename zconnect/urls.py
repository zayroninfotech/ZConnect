from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', lambda r: redirect('login'), name='index'),
    path('', include('accounts.urls')),
    path('', include('workspace.urls')),
    path('', include('messaging.urls')),
    path('', include('calls.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
