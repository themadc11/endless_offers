from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_notificaciones, name='lista_notificaciones'),
    path('marcar-leido/<int:notificacion_id>/', views.marcar_como_leido, name='marcar_notificacion_leido'),
    path('marcar-todas-leido/', views.marcar_todas_como_leidas, name='marcar_todas_leidas'),
]