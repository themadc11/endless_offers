from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from ofertas import views as ofertas_views
from django.views.generic import TemplateView
from django.views.generic import RedirectView

# PERSONALIZACIÓN DEL ADMIN
admin.site.site_header = "Panel Administrativo - EndlessOffers"
admin.site.site_title = "EndlessOffers Admin"
admin.site.index_title = "Gestión de la Plataforma"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel-admin/', include('admin_panel.urls')),
    path('', ofertas_views.home, name='home'),
    path('ofertas/', include('ofertas.urls')),
    path('usuarios/', include('usuarios.urls')),
    
    # 👇 PRIMERO: Redirigir accounts/login a tu login (específico)
    path('accounts/login/', RedirectView.as_view(url='/usuarios/login/', permanent=True)),
    
    # 👇 DESPUÉS: Incluir el resto de URLs de auth (password_change, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Proveedores
    path('proveedores/', ofertas_views.lista_proveedores, name='lista_proveedores'),
    path('proveedor/<str:username>/', ofertas_views.perfil_proveedor, name='perfil_proveedor'),
    
    # Páginas estáticas
    path('terminos/', TemplateView.as_view(template_name='usuarios/terminos.html'), name='terminos'),
    path('acerca-de/', TemplateView.as_view(template_name='usuarios/acerca_de.html'), name='acerca-de'),
    
    path('notificaciones/', include('notificaciones.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)