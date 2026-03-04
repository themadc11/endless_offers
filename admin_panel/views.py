from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from ofertas.models import Oferta, Categoria, Comentario, Calificacion, Favorito
from ofertas.forms import OfertaForm
from usuarios.models import Perfil, SolicitudProveedor

# ==================== DASHBOARD ====================

@staff_member_required
def dashboard_admin(request):
    """Dashboard principal del panel administrativo"""
    
    # Estadísticas generales
    total_usuarios = User.objects.count()
    total_proveedores = Perfil.objects.filter(rol='proveedor').count()
    total_ofertas = Oferta.objects.count()
    ofertas_pendientes = Oferta.objects.filter(estado='pendiente').count()
    
    # Solicitudes pendientes
    solicitudes_pendientes = SolicitudProveedor.objects.filter(estado='pendiente').count()
    
    # Últimas actividades
    ultimas_solicitudes = SolicitudProveedor.objects.order_by('-fecha_solicitud')[:5]
    ultimas_ofertas = Oferta.objects.order_by('-fecha_creacion')[:5]
    ultimos_usuarios = User.objects.order_by('-date_joined')[:5]
    
    # Gráficos (datos para últimos 7 días)
    dias = []
    solicitudes_data = []
    ofertas_data = []
    
    for i in range(6, -1, -1):
        dia = timezone.now() - timedelta(days=i)
        dias.append(dia.strftime('%d/%m'))
        
        solicitudes_dia = SolicitudProveedor.objects.filter(
            fecha_solicitud__date=dia.date()
        ).count()
        solicitudes_data.append(solicitudes_dia)
        
        ofertas_dia = Oferta.objects.filter(
            fecha_creacion__date=dia.date()
        ).count()
        ofertas_data.append(ofertas_dia)
    
    # Contadores para el sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        # Estadísticas
        'total_usuarios': total_usuarios,
        'total_proveedores': total_proveedores,
        'total_ofertas': total_ofertas,
        'ofertas_pendientes': ofertas_pendientes,
        'solicitudes_pendientes': solicitudes_pendientes,
        
        # Listas recientes
        'ultimas_solicitudes': ultimas_solicitudes,
        'ultimas_ofertas': ultimas_ofertas,
        'ultimos_usuarios': ultimos_usuarios,
        
        # Datos para gráficos
        'dias': dias,
        'solicitudes_data': solicitudes_data,
        'ofertas_data': ofertas_data,
        
        # Fecha actual
        'now': timezone.now(),
        
        # Contadores para el sidebar
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


# ==================== SOLICITUDES PROVEEDOR ====================

@staff_member_required
def solicitudes_proveedores(request):
    """Lista de solicitudes de proveedor"""
    solicitudes = SolicitudProveedor.objects.all().order_by('-fecha_solicitud')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    
    # Contadores para el sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'solicitudes': solicitudes,
        'estado_actual': estado,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/solicitudes_proveedores.html', context)


@staff_member_required
def procesar_solicitud_proveedor(request, solicitud_id, accion):
    """Aprobar o rechazar solicitud de proveedor"""
    solicitud = get_object_or_404(SolicitudProveedor, id=solicitud_id)
    
    if accion == 'aprobar':
        solicitud.estado = 'aprobada'
        solicitud.save()
        
        # Cambiar rol del usuario
        perfil = solicitud.usuario.perfil
        perfil.rol = 'proveedor'
        perfil.verificado = True  # Marcar como verificado
        perfil.save()
        
        messages.success(request, f'✅ Solicitud de {solicitud.usuario.username} aprobada correctamente.')
        
    elif accion == 'rechazar':
        solicitud.estado = 'rechazada'
        solicitud.save()
        messages.warning(request, f'⚠️ Solicitud de {solicitud.usuario.username} rechazada.')
    
    return redirect('admin_solicitudes_proveedores')


@staff_member_required
def eliminar_solicitud(request, solicitud_id):
    """Eliminar solicitud de proveedor"""
    if request.method == 'POST':
        solicitud = get_object_or_404(SolicitudProveedor, id=solicitud_id)
        usuario = solicitud.usuario.username
        estado = solicitud.estado
        
        solicitud.delete()
        messages.success(request, f'✅ Solicitud de "{usuario}" (estado: {estado}) eliminada.')
    
    return redirect('admin_solicitudes_proveedores')


# ==================== OFERTAS ====================

@staff_member_required
def lista_ofertas_admin(request):
    """Lista completa de ofertas para administrar"""
    ofertas = Oferta.objects.all().order_by('-fecha_creacion')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        ofertas = ofertas.filter(estado=estado)
    
    proveedor_id = request.GET.get('proveedor')
    if proveedor_id:
        ofertas = ofertas.filter(proveedor_id=proveedor_id)
    
    # Buscador
    buscar = request.GET.get('buscar')
    if buscar:
        ofertas = ofertas.filter(
            Q(titulo__icontains=buscar) | 
            Q(descripcion__icontains=buscar)
        )
    
    # Contadores
    total_ofertas = ofertas.count()
    ofertas_pendientes = Oferta.objects.filter(estado='pendiente').count()
    ofertas_activas = Oferta.objects.filter(estado='activa').count()
    ofertas_rechazadas = Oferta.objects.filter(estado='rechazada').count()
    
    # Paginación
    paginator = Paginator(ofertas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contadores para sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'ofertas': page_obj,
        'total_ofertas': total_ofertas,
        'ofertas_pendientes': ofertas_pendientes,
        'ofertas_activas': ofertas_activas,
        'ofertas_rechazadas': ofertas_rechazadas,
        'estado_actual': estado,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/ofertas_lista.html', context)


@staff_member_required
def ofertas_pendientes(request):
    """Lista de ofertas pendientes de revisión"""
    ofertas = Oferta.objects.filter(estado='pendiente').order_by('-fecha_creacion')
    
    # Contadores para el sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'ofertas': ofertas,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/ofertas_pendientes.html', context)


@staff_member_required
def detalle_oferta_admin(request, oferta_id):
    """Ver detalle completo de una oferta"""
    oferta = get_object_or_404(Oferta, id=oferta_id)
    
    # Estadísticas de la oferta
    total_favoritos = Favorito.objects.filter(oferta=oferta).count()
    total_comentarios = Comentario.objects.filter(oferta=oferta).count()
    total_calificaciones = Calificacion.objects.filter(oferta=oferta).count()
    promedio_calificacion = Calificacion.objects.filter(oferta=oferta).aggregate(Avg('puntuacion'))['puntuacion__avg']
    
    # Contadores para sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'oferta': oferta,
        'total_favoritos': total_favoritos,
        'total_comentarios': total_comentarios,
        'total_calificaciones': total_calificaciones,
        'promedio_calificacion': promedio_calificacion,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/ofertas_detalle.html', context)


@staff_member_required
def editar_oferta_admin(request, oferta_id):
    """Editar oferta desde el panel admin"""
    oferta = get_object_or_404(Oferta, id=oferta_id)
    
    if request.method == 'POST':
        # Limpiar puntos de los precios
        datos_post = request.POST.copy()
        if 'precio_original' in datos_post:
            datos_post['precio_original'] = datos_post['precio_original'].replace('.', '')
        if 'precio_descuento' in datos_post:
            datos_post['precio_descuento'] = datos_post['precio_descuento'].replace('.', '')
        
        form = OfertaForm(datos_post, request.FILES, instance=oferta)
        if form.is_valid():
            oferta = form.save(commit=False)
            
            # Recalcular porcentaje
            if oferta.precio_original > 0:
                oferta.porcentaje_descuento = (
                    (oferta.precio_original - oferta.precio_descuento) / oferta.precio_original
                ) * 100
            
            oferta.save()
            form.save_m2m()
            messages.success(request, f'✅ Oferta "{oferta.titulo}" actualizada correctamente.')
            return redirect('admin_detalle_oferta', oferta_id=oferta.id)
        else:
            messages.error(request, '❌ Error al actualizar. Verifica los datos.')
    else:
        form = OfertaForm(instance=oferta)
    
    # Contadores para sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'form': form,
        'oferta': oferta,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/ofertas_editar.html', context)


@staff_member_required
def aprobar_oferta(request, oferta_id):
    """Aprobar oferta pendiente"""
    oferta = get_object_or_404(Oferta, id=oferta_id)
    
    if oferta.estado == 'pendiente':
        oferta.estado = 'activa'
        oferta.save()
        messages.success(request, f'✅ Oferta "{oferta.titulo}" aprobada correctamente.')
    else:
        messages.warning(request, f'⚠️ La oferta no está pendiente (estado actual: {oferta.estado})')
    
    return redirect('admin_ofertas_pendientes')


@staff_member_required
def rechazar_oferta(request, oferta_id):
    """Rechazar oferta pendiente"""
    oferta = get_object_or_404(Oferta, id=oferta_id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        
        oferta.estado = 'rechazada'
        oferta.save()
        
        # Opcional: guardar motivo o enviar notificación
        messages.warning(request, f'⚠️ Oferta "{oferta.titulo}" rechazada.')
    
    return redirect('admin_ofertas_pendientes')


@staff_member_required
def eliminar_oferta_admin(request, oferta_id):
    """Eliminar oferta definitivamente"""
    oferta = get_object_or_404(Oferta, id=oferta_id)
    
    if request.method == 'POST':
        titulo = oferta.titulo
        oferta.delete()
        messages.success(request, f'✅ Oferta "{titulo}" eliminada correctamente.')
    
    return redirect('admin_ofertas')


# ==================== USUARIOS ====================

@staff_member_required
def lista_usuarios(request):
    """Lista de usuarios para administrar"""
    usuarios = User.objects.all().order_by('-date_joined')
    
    # Filtro por rol
    rol = request.GET.get('rol')
    if rol:
        usuarios = usuarios.filter(perfil__rol=rol)
    
    # Buscador
    buscar = request.GET.get('buscar')
    if buscar:
        usuarios = usuarios.filter(
            Q(username__icontains=buscar) | 
            Q(email__icontains=buscar) |
            Q(perfil__nombre_completo__icontains=buscar)
        )
    
    # Contadores para el sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    # Paginación
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'usuarios': page_obj,
        'rol_actual': rol,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/usuarios.html', context)


@staff_member_required
def detalle_usuario(request, user_id):
    """Ver detalle completo de un usuario"""
    usuario = get_object_or_404(User, id=user_id)
    
    # Estadísticas
    total_ofertas = Oferta.objects.filter(proveedor=usuario.perfil).count()
    ofertas_activas = Oferta.objects.filter(proveedor=usuario.perfil, estado='activa').count()
    total_comentarios = Comentario.objects.filter(usuario=usuario).count()
    total_favoritos = Favorito.objects.filter(usuario=usuario).count()
    
    # Contadores para sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'usuario': usuario,
        'perfil': usuario.perfil,
        'total_ofertas': total_ofertas,
        'ofertas_activas': ofertas_activas,
        'total_comentarios': total_comentarios,
        'total_favoritos': total_favoritos,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/usuario_detalle.html', context)


@staff_member_required
def editar_usuario(request, user_id):
    """Editar usuario desde admin"""
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Actualizar campos básicos
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name = request.POST.get('last_name', '')
        usuario.email = request.POST.get('email', usuario.email)
        usuario.is_active = 'is_active' in request.POST
        usuario.is_staff = 'is_staff' in request.POST
        
        # Actualizar perfil
        usuario.perfil.nombre_completo = request.POST.get('nombre_completo', '')
        usuario.perfil.telefono = request.POST.get('telefono', '')
        usuario.perfil.direccion = request.POST.get('direccion', '')
        usuario.perfil.descripcion = request.POST.get('descripcion', '')
        usuario.perfil.rol = request.POST.get('rol', usuario.perfil.rol)
        usuario.perfil.verificado = 'verificado' in request.POST
        
        usuario.save()
        usuario.perfil.save()
        
        messages.success(request, f'✅ Usuario {usuario.username} actualizado.')
        return redirect('admin_detalle_usuario', user_id=usuario.id)
    
    # Contadores para sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'usuario': usuario,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/usuario_editar.html', context)


@staff_member_required
def cambiar_rol_usuario(request, user_id):
    """Cambiar rol de usuario (admin)"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        nuevo_rol = request.POST.get('rol')
        
        if nuevo_rol in ['consumidor', 'proveedor']:
            user.perfil.rol = nuevo_rol
            user.perfil.save()
            messages.success(request, f'✅ Rol de {user.username} actualizado a {nuevo_rol}.')
    
    return redirect('admin_usuarios')


@staff_member_required
def verificar_proveedor(request, user_id):
    """Verificar a un proveedor manualmente"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        if user.perfil.rol != 'proveedor':
            messages.warning(request, f'⚠️ {user.username} no es un proveedor.')
            return redirect('admin_usuarios')
        
        user.perfil.verificado = True
        user.perfil.save()
        messages.success(request, f'✅ {user.username} ahora es un proveedor verificado.')
    
    return redirect('admin_usuarios')


@staff_member_required
def eliminar_usuario(request, user_id):
    """Eliminar usuario permanentemente"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # No permitir eliminarse a sí mismo
        if user == request.user:
            messages.error(request, '❌ No puedes eliminarte a ti mismo.')
            return redirect('admin_usuarios')
        
        username = user.username
        rol = user.perfil.rol
        
        user.delete()
        messages.success(request, f'✅ Usuario "{username}" ({rol}) eliminado correctamente.')
    
    return redirect('admin_usuarios')


# ==================== CATEGORÍAS ====================

@staff_member_required
def lista_categorias(request):
    """CRUD de categorías"""
    categorias = Categoria.objects.annotate(
        total_ofertas=Count('oferta')
    ).order_by('nombre')
    
    # Contadores para el sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'categorias': categorias,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/categorias.html', context)


@staff_member_required
def crear_categoria(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        imagen = request.FILES.get('imagen')
        if nombre:
            categoria = Categoria.objects.create(nombre=nombre)
            if imagen:
                categoria.imagen = imagen
                categoria.save()
            messages.success(request, f'✅ Categoría "{nombre}" creada correctamente.')
            return redirect('admin_categorias')
    
    # Contadores para el sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/crear_categoria.html', context)


@staff_member_required
def editar_categoria(request, categoria_id):
    """Editar categoría"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre')
        nueva_imagen = request.FILES.get('imagen')
        
        if nuevo_nombre:
            categoria.nombre = nuevo_nombre
        
        if nueva_imagen:
            categoria.imagen = nueva_imagen
        
        categoria.save()
        messages.success(request, f'✅ Categoría actualizada a "{nuevo_nombre}".')
        return redirect('admin_categorias')
    
    # Contadores para el sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    context = {
        'categoria': categoria,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/editar_categoria.html', context)


@staff_member_required
def eliminar_categoria(request, categoria_id):
    """Eliminar categoría con verificación"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        nombre = categoria.nombre
        ofertas_asociadas = categoria.oferta_set.count()
        
        if ofertas_asociadas > 0:
            messages.warning(request, f'⚠️ No se puede eliminar "{nombre}" porque tiene {ofertas_asociadas} ofertas asociadas.')
        else:
            categoria.delete()
            messages.success(request, f'✅ Categoría "{nombre}" eliminada correctamente.')
    
    return redirect('admin_categorias')


# ==================== COMENTARIOS ====================

@staff_member_required
def lista_comentarios(request):
    """Lista de todos los comentarios para gestionar"""
    comentarios = Comentario.objects.all().order_by('-fecha_creacion')
    
    # Filtros
    oferta_id = request.GET.get('oferta')
    usuario_id = request.GET.get('usuario')
    
    if oferta_id:
        comentarios = comentarios.filter(oferta_id=oferta_id)
    if usuario_id:
        comentarios = comentarios.filter(usuario_id=usuario_id)
    
    # Contadores para el sidebar
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    # Paginación
    paginator = Paginator(comentarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'comentarios': page_obj,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/comentarios.html', context)


@staff_member_required
def eliminar_comentario(request, comentario_id):
    """Eliminar comentario"""
    if request.method == 'POST':
        comentario = get_object_or_404(Comentario, id=comentario_id)
        contenido = comentario.contenido[:50]
        autor = comentario.usuario.username
        
        comentario.delete()
        messages.success(request, f'✅ Comentario de "{autor}" eliminado: "{contenido}..."')
    
    return redirect('admin_comentarios')


# ==================== CALIFICACIONES ====================

@staff_member_required
def lista_calificaciones(request):
    """Lista de todas las calificaciones"""
    calificaciones = Calificacion.objects.all().order_by('-fecha_creacion')
    
    # Contadores
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    # Paginación
    paginator = Paginator(calificaciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'calificaciones': page_obj,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/calificaciones.html', context)


@staff_member_required
def eliminar_calificacion(request, calificacion_id):
    """Eliminar calificación"""
    if request.method == 'POST':
        calificacion = get_object_or_404(Calificacion, id=calificacion_id)
        usuario = calificacion.usuario.username
        oferta = calificacion.oferta.titulo
        puntuacion = calificacion.puntuacion
        
        calificacion.delete()
        messages.success(request, f'✅ Calificación de {puntuacion}★ de "{usuario}" eliminada.')
    
    return redirect('admin_calificaciones')


# ==================== FAVORITOS ====================

@staff_member_required
def lista_favoritos(request):
    """Lista de todos los favoritos"""
    favoritos = Favorito.objects.all().order_by('-fecha')
    
    # Contadores
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(estado='pendiente').count()
    ofertas_pendientes_count = Oferta.objects.filter(estado='pendiente').count()
    
    # Paginación
    paginator = Paginator(favoritos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'favoritos': page_obj,
        'now': timezone.now(),
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'ofertas_pendientes_count': ofertas_pendientes_count,
    }
    return render(request, 'admin_panel/favoritos.html', context)


@staff_member_required
def eliminar_favorito(request, favorito_id):
    """Eliminar favorito"""
    if request.method == 'POST':
        favorito = get_object_or_404(Favorito, id=favorito_id)
        usuario = favorito.usuario.username
        oferta = favorito.oferta.titulo
        
        favorito.delete()
        messages.success(request, f'✅ Favorito de "{usuario}" en "{oferta}" eliminado.')
    
    return redirect('admin_favoritos')