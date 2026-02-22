from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# 👇 PERSONALIZACIÓN DEL ADMIN
admin.site.site_header = "Panel Administrativo - EndlessOffers"
admin.site.site_title = "EndlessOffers Admin"
admin.site.index_title = "Gestión de la Plataforma"

urlpatterns = [
    path('admin/', admin.site.urls),

    # La app ofertas ahora vive en la raíz
    path('', include('ofertas.urls')),

    path('accounts/', include('django.contrib.auth.urls')),
    path('usuarios/', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)