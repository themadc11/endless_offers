from .models import Notificacion

def notificaciones(request):
    """Context processor para mostrar notificaciones en toda la página"""
    if request.user.is_authenticated:
        notificaciones_no_leidas = Notificacion.objects.filter(
            usuario=request.user,
            leido=False
        ).order_by('-fecha_creacion')[:10]
        
        count_no_leidas = Notificacion.objects.filter(
            usuario=request.user,
            leido=False
        ).count()
        
        # También obtener las últimas 5 notificaciones (incluyendo leídas) para el dropdown
        ultimas_notificaciones = Notificacion.objects.filter(
            usuario=request.user
        ).order_by('-fecha_creacion')[:5]
        
        return {
            'notificaciones': ultimas_notificaciones,
            'notificaciones_no_leidas': notificaciones_no_leidas,
            'notificaciones_count': count_no_leidas,
        }
    return {
        'notificaciones': [],
        'notificaciones_no_leidas': [],
        'notificaciones_count': 0,
    }