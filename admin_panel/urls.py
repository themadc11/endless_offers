from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_admin, name='admin_dashboard'),
    
    # ===== SOLICITUDES DE PROVEEDORES =====
    path('solicitudes/', views.solicitudes_proveedores, name='admin_solicitudes_proveedores'),
    # 👇 ESPECÍFICAS PRIMERO
    path('solicitudes/<int:solicitud_id>/detalle/', views.detalle_solicitud, name='detalle_solicitud'),
    path('solicitudes/<int:solicitud_id>/eliminar/', views.eliminar_solicitud, name='eliminar_solicitud'),
    # 👇 GENÉRICA AL FINAL (la que tiene <str:accion>)
    path('solicitudes/<int:solicitud_id>/<str:accion>/', views.procesar_solicitud_proveedor, name='procesar_solicitud_proveedor'),
    
    # ===== OFERTAS =====
    path('ofertas/', views.lista_ofertas_admin, name='admin_ofertas'),
    path('ofertas/pendientes/', views.ofertas_pendientes, name='admin_ofertas_pendientes'),
    # 👇 ESPECÍFICAS PRIMERO
    path('ofertas/<int:oferta_id>/', views.detalle_oferta_admin, name='admin_detalle_oferta'),
    path('ofertas/<int:oferta_id>/editar/', views.editar_oferta_admin, name='admin_editar_oferta'),
    path('ofertas/<int:oferta_id>/aprobar/', views.aprobar_oferta, name='admin_aprobar_oferta'),
    path('ofertas/<int:oferta_id>/rechazar/', views.rechazar_oferta, name='admin_rechazar_oferta'),
    path('ofertas/<int:oferta_id>/eliminar/', views.eliminar_oferta_admin, name='admin_eliminar_oferta'),
    
    # ===== USUARIOS =====
    path('usuarios/', views.lista_usuarios, name='admin_usuarios'),
    # 👇 ESPECÍFICAS PRIMERO
    path('usuarios/<int:user_id>/', views.detalle_usuario, name='admin_detalle_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='admin_editar_usuario'),
    path('usuarios/<int:user_id>/cambiar-rol/', views.cambiar_rol_usuario, name='cambiar_rol_usuario'),
    path('usuarios/<int:user_id>/verificar/', views.verificar_proveedor, name='verificar_proveedor'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # ===== CATEGORÍAS =====
    path('categorias/', views.lista_categorias, name='admin_categorias'),
    path('categorias/crear/', views.crear_categoria, name='admin_crear_categoria'),
    path('categorias/<int:categoria_id>/editar/', views.editar_categoria, name='admin_editar_categoria'),
    path('categorias/<int:categoria_id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # ===== COMENTARIOS =====
    path('comentarios/', views.lista_comentarios, name='admin_comentarios'),
    path('comentarios/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
    
    # ===== CALIFICACIONES =====
    path('calificaciones/', views.lista_calificaciones, name='admin_calificaciones'),
    path('calificaciones/<int:calificacion_id>/eliminar/', views.eliminar_calificacion, name='eliminar_calificacion'),
    
    # ===== FAVORITOS =====
    path('favoritos/', views.lista_favoritos, name='admin_favoritos'),
    path('favoritos/<int:favorito_id>/eliminar/', views.eliminar_favorito, name='eliminar_favorito'),
]