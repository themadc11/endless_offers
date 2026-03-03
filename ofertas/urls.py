from django.urls import path
from . import views

urlpatterns = [
    # Lista de ofertas en /ofertas/
    path('', views.lista_ofertas, name='lista_ofertas'),
    
    # Detalle de oferta en /ofertas/oferta/1/
    path('oferta/<int:oferta_id>/', views.detalle_oferta, name='detalle_oferta'),
    
    # Crear oferta en /ofertas/crear/
    path('crear/', views.crear_oferta, name='crear_oferta'),
    
    # Mis ofertas en /ofertas/mis-ofertas/
    path('mis-ofertas/', views.mis_ofertas, name='mis_ofertas'),
    
    # Editar oferta en /ofertas/editar/1/
    path('editar/<int:oferta_id>/', views.editar_oferta, name='editar_oferta'),
    
    # Toggle favorito en /ofertas/favorito/1/
    path("favorito/<int:oferta_id>/", views.toggle_favorito, name="toggle_favorito"),
    
    # Mis favoritos en /ofertas/mis-favoritos/
    path("mis-favoritos/", views.mis_favoritos, name="mis_favoritos"),
    
    # Eliminar oferta en /ofertas/eliminar/1/
    path("eliminar/<int:oferta_id>/", views.eliminar_oferta, name="eliminar_oferta"),
    
    # Dashboard proveedor en /ofertas/dashboard/
    path("dashboard/", views.dashboard_proveedor, name="dashboard_proveedor"),
]