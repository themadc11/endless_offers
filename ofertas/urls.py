from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ofertas, name='lista_ofertas'),
    path('oferta/<int:oferta_id>/', views.detalle_oferta, name='detalle_oferta'),
    path('crear/', views.crear_oferta, name='crear_oferta'),
    path('mis-ofertas/', views.mis_ofertas, name='mis_ofertas'),
    path('editar/<int:oferta_id>/', views.editar_oferta, name='editar_oferta'),
    path("favorito/<int:oferta_id>/", views.toggle_favorito, name="toggle_favorito"),
    path("mis-favoritos/", views.mis_favoritos, name="mis_favoritos"),
    path("eliminar/<int:oferta_id>/", views.eliminar_oferta, name="eliminar_oferta"),
    path("dashboard/", views.dashboard_proveedor, name="dashboard_proveedor"),
    
]
