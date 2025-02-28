from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Keep admin URLs
    path('', include('joo.urls')),    # Include your app's URLs
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# For serving media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 