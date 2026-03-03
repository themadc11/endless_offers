from .models import Notificacion

def notificaciones(request):
    if request.user.is_authenticated:
        notificaciones_no_leidas = Notificacion.objects.filter(
            usuario=request.user,
            leido=False
        ).order_by('-fecha_creacion')[:10]
        
        count_no_leidas = Notificacion.objects.filter(
            usuario=request.user,
            leido=False
        ).count()
        
        return {
            'notificaciones': notificaciones_no_leidas,
            'notificaciones_count': count_no_leidas,
        }
    return {
        'notificaciones': [],
        'notificaciones_count': 0,
    }