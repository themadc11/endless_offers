from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # Autenticación - Usamos login_view en lugar de login
    path('login/', views.login_view, name='login'),  # Cambiado a login_view
    path('registro/', views.registro, name='registro'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Perfil - AHORA SÍ EXISTE LA VISTA 'perfil'
    path('perfil/', views.perfil, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    
    # Solicitudes
    path('solicitar-proveedor/', views.solicitar_proveedor, name='solicitar_proveedor'),
    
    # Recuperación de contraseña
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), 
         name='password_reset_complete'),
]