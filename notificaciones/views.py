from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notificacion

@login_required
def lista_notificaciones(request):
    """Lista todas las notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')
    
    return render(request, 'notificaciones/lista.html', {
        'notificaciones': notificaciones
    })


@login_required
def marcar_como_leido(request, notificacion_id):
    """Marca una notificación como leída"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leido = True
    notificacion.save()
    
    if notificacion.link:
        return redirect(notificacion.link)
    return redirect('lista_notificaciones')


@login_required
def marcar_todas_como_leidas(request):
    """Marca todas las notificaciones del usuario como leídas"""
    Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    return redirect('lista_notificaciones')