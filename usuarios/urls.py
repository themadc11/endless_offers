from django.urls import path
from . import views

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("ser-proveedor/", views.ser_proveedor, name="ser_proveedor"),
    path("registro/", views.registro, name="registro"),
    path('perfil/', views.perfil, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('solicitar-proveedor/', views.solicitar_proveedor, name='solicitar_proveedor'),

]