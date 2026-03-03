from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_admin, name='admin_dashboard'),
    path('solicitudes/', views.solicitudes_proveedores, name='admin_solicitudes_proveedores'),
    path('solicitudes/<int:solicitud_id>/<str:accion>/', views.procesar_solicitud_proveedor, name='procesar_solicitud_proveedor'),
    path('solicitudes/<int:solicitud_id>/eliminar/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('ofertas-pendientes/', views.ofertas_pendientes, name='admin_ofertas_pendientes'),
    path('ofertas/<int:oferta_id>/<str:accion>/', views.procesar_oferta, name='procesar_oferta'),
    path('ofertas/<int:oferta_id>/eliminar/', views.eliminar_oferta_admin, name='eliminar_oferta_admin'),
    path('usuarios/', views.lista_usuarios, name='admin_usuarios'),
    path('usuarios/<int:user_id>/cambiar-rol/', views.cambiar_rol_usuario, name='cambiar_rol_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('categorias/', views.lista_categorias, name='admin_categorias'),
    path('categorias/crear/', views.crear_categoria, name='admin_crear_categoria'),
    path('categorias/<int:categoria_id>/editar/', views.editar_categoria, name='admin_editar_categoria'),
    path('categorias/<int:categoria_id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    path('comentarios/', views.lista_comentarios, name='admin_comentarios'),
    path('comentarios/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
    path('calificaciones/', views.lista_calificaciones, name='admin_calificaciones'),
    path('calificaciones/<int:calificacion_id>/eliminar/', views.eliminar_calificacion, name='eliminar_calificacion'),
    path('favoritos/', views.lista_favoritos, name='admin_favoritos'),
    path('favoritos/<int:favorito_id>/eliminar/', views.eliminar_favorito, name='eliminar_favorito'),
    path('usuarios/<int:user_id>/verificar/', views.verificar_proveedor, name='verificar_proveedor'),

]