from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from ofertas import views as ofertas_views
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views  # 👈 Agrega esto

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
    
    # Redirigir accounts/login a tu login
    path('accounts/login/', RedirectView.as_view(url='/usuarios/login/', permanent=True)),
    
    # 👇 URLs de auth PERSONALIZADAS (solo las que necesitas)
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    # 👇 NO incluyas password_reset aquí
    
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