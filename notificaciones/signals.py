from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from ofertas.models import Oferta, Comentario, Calificacion, Favorito
from usuarios.models import SolicitudProveedor
from .models import Notificacion

# ==================== NOTIFICACIONES PARA ADMIN ====================

@receiver(post_save, sender=SolicitudProveedor)
def notificar_solicitud_proveedor(sender, instance, created, **kwargs):
    """Notificar al admin cuando hay una nueva solicitud de proveedor"""
    if created:
        # Obtener todos los admins
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notificacion.objects.create(
                usuario=admin,
                tipo='solicitud_proveedor',
                titulo='Nueva solicitud de proveedor',
                mensaje=f'{instance.usuario.username} ha solicitado ser proveedor.',
                link=reverse('admin_solicitudes_proveedores')
            )


@receiver(post_save, sender=Oferta)
def notificar_nueva_oferta(sender, instance, created, **kwargs):
    """Notificar al admin cuando se crea una nueva oferta"""
    if created and instance.estado == 'pendiente':
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notificacion.objects.create(
                usuario=admin,
                tipo='nueva_oferta',
                titulo='Nueva oferta pendiente',
                mensaje=f'{instance.proveedor.user.username} ha creado una nueva oferta: {instance.titulo}',
                link=reverse('admin_ofertas_pendientes')
            )


# ==================== NOTIFICACIONES PARA PROVEEDORES ====================

@receiver(pre_save, sender=SolicitudProveedor)
def notificar_estado_solicitud(sender, instance, **kwargs):
    """Notificar al proveedor cuando su solicitud es aprobada o rechazada"""
    if instance.pk:  # Si ya existe (está siendo actualizada)
        try:
            old = SolicitudProveedor.objects.get(pk=instance.pk)
            if old.estado != instance.estado:  # Si cambió el estado
                if instance.estado == 'aprobada':
                    # También marcar como verificado
                    perfil = instance.usuario.perfil
                    perfil.verificado = True
                    perfil.save()
                    
                    Notificacion.objects.create(
                        usuario=instance.usuario,
                        tipo='aprobacion_proveedor',
                        titulo='¡Solicitud aprobada!',
                        mensaje='Felicidades, ahora eres un proveedor verificado. Ya puedes crear ofertas.',
                        link=reverse('dashboard_proveedor')
                    )
                elif instance.estado == 'rechazada':
                    Notificacion.objects.create(
                        usuario=instance.usuario,
                        tipo='rechazo_proveedor',
                        titulo='Solicitud rechazada',
                        mensaje='Tu solicitud para ser proveedor ha sido rechazada. Puedes volver a intentarlo.',
                        link=reverse('perfil')
                    )
        except SolicitudProveedor.DoesNotExist:
            pass


@receiver(pre_save, sender=Oferta)
def notificar_estado_oferta(sender, instance, **kwargs):
    """Notificar al proveedor cuando su oferta es aprobada o rechazada"""
    if instance.pk:
        try:
            old = Oferta.objects.get(pk=instance.pk)
            if old.estado != instance.estado:
                if instance.estado == 'activa':
                    Notificacion.objects.create(
                        usuario=instance.proveedor.user,
                        tipo='aprobacion_oferta',
                        titulo='¡Oferta aprobada!',
                        mensaje=f'Tu oferta "{instance.titulo}" ha sido aprobada y ya está visible.',
                        link=reverse('detalle_oferta', args=[instance.id])
                    )
                elif instance.estado == 'rechazada':
                    Notificacion.objects.create(
                        usuario=instance.proveedor.user,
                        tipo='rechazo_oferta',
                        titulo='Oferta rechazada',
                        mensaje=f'Tu oferta "{instance.titulo}" ha sido rechazada. Por favor revísala.',
                        link=reverse('mis_ofertas')
                    )
        except Oferta.DoesNotExist:
            pass


@receiver(post_save, sender=Comentario)
def notificar_nuevo_comentario(sender, instance, created, **kwargs):
    """Notificar al proveedor cuando alguien comenta en su oferta"""
    if created:
        proveedor = instance.oferta.proveedor.user
        if proveedor != instance.usuario:  # No notificar si el comentario es del mismo proveedor
            Notificacion.objects.create(
                usuario=proveedor,
                tipo='nuevo_comentario',
                titulo='Nuevo comentario',
                mensaje=f'{instance.usuario.username} comentó en tu oferta "{instance.oferta.titulo}": {instance.contenido[:50]}...',
                link=reverse('detalle_oferta', args=[instance.oferta.id])
            )


@receiver(post_save, sender=Calificacion)
def notificar_nueva_calificacion(sender, instance, created, **kwargs):
    """Notificar al proveedor cuando alguien califica su oferta"""
    if created:
        proveedor = instance.oferta.proveedor.user
        if proveedor != instance.usuario:
            Notificacion.objects.create(
                usuario=proveedor,
                tipo='nueva_calificacion',
                titulo='Nueva calificación',
                mensaje=f'{instance.usuario.username} calificó tu oferta "{instance.oferta.titulo}" con {instance.puntuacion} estrellas.',
                link=reverse('detalle_oferta', args=[instance.oferta.id])
            )


@receiver(post_save, sender=Favorito)
def notificar_nuevo_favorito(sender, instance, created, **kwargs):
    """Notificar al proveedor cuando alguien agrega su oferta a favoritos"""
    if created:
        proveedor = instance.oferta.proveedor.user
        if proveedor != instance.usuario:
            Notificacion.objects.create(
                usuario=proveedor,
                tipo='nuevo_favorito',
                titulo='Nuevo favorito',
                mensaje=f'{instance.usuario.username} agregó tu oferta "{instance.oferta.titulo}" a favoritos.',
                link=reverse('detalle_oferta', args=[instance.oferta.id])
            )