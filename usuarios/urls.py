from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView  # 👈 NUEVA IMPORTACIÓN
from . import views
from .views import CustomPasswordResetView

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Perfil
    path('perfil/', views.perfil, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    
    # Solicitudes
    path('solicitar-proveedor/', views.solicitar_proveedor, name='solicitar_proveedor'),
    
    # Recuperación de contraseña
    path('password-reset/', 
         CustomPasswordResetView.as_view(),
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='usuarios/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='usuarios/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='usuarios/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # ✅ Términos y condiciones (nuevo)
    path('terminos/', TemplateView.as_view(template_name='usuarios/terminos.html'), name='terminos'),
]