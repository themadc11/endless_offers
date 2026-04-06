from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Notificacion

@login_required
def lista_notificaciones(request):
    """Lista todas las notificaciones del usuario con paginación"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(notificaciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notificaciones/lista.html', {
        'notificaciones': page_obj,
        'page_obj': page_obj
    })


@login_required
def marcar_como_leido(request, notificacion_id):
    """Marca una notificación como leída"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leido = True
    notificacion.save()
    
    # Si la notificación tiene un link, redirigir a él
    if notificacion.link:
        return redirect(notificacion.link)
    return redirect('lista_notificaciones')


@login_required
def marcar_todas_como_leidas(request):
    """Marca todas las notificaciones del usuario como leídas"""
    count = Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    if count > 0:
        messages.success(request, f'{count} notificaciones marcadas como leídas.')
    else:
        messages.info(request, 'No tienes notificaciones sin leer.')
    return redirect('lista_notificaciones')