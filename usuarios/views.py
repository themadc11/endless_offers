from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login  # Renombrado para evitar conflicto
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta

from .forms import RegistroForm, PerfilForm
from .models import Perfil, SolicitudProveedor

# ==================== AUTENTICACIÓN ====================

def login_view(request):  # Cambié el nombre de 'login' a 'login_view'
    """Vista personalizada de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('lista_ofertas')
    
    return auth_views.LoginView.as_view(
        template_name='usuarios/login.html',
        redirect_authenticated_user=True
    )(request)


def registro(request):
    """Registro de nuevo usuario"""
    if request.user.is_authenticated:
        return redirect('lista_ofertas')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


# ==================== PERFIL ====================

@login_required
def perfil(request):
    """Vista del perfil del usuario"""
    perfil = request.user.perfil
    solicitud = SolicitudProveedor.objects.filter(
        usuario=request.user
    ).order_by('-fecha_solicitud').first()
    
    # Si es proveedor, obtenemos datos extra
    if perfil.rol == 'proveedor':
        from ofertas.models import Oferta, Calificacion
        
        ofertas_activas = Oferta.objects.filter(
            proveedor=request.user, 
            estado='activa'
        ).count()
        
        # Calcular reputación
        calificaciones = Calificacion.objects.filter(
            oferta__proveedor=request.user
        ).aggregate(
            promedio=Avg('puntuacion'),
            total=Count('id')
        )
        
        context = {
            "perfil": perfil,
            "solicitud": solicitud,
            "ofertas_activas": ofertas_activas,
            "reputacion": {
                'promedio': round(calificaciones['promedio'], 1) if calificaciones['promedio'] else 0,
                'total': calificaciones['total'] or 0
            }
        }
    else:
        context = {
            "perfil": perfil,
            "solicitud": solicitud
        }
    
    return render(request, "usuarios/perfil.html", context)


@login_required
def editar_perfil(request):
    """Editar perfil de usuario"""
    perfil = request.user.perfil

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Perfil actualizado correctamente.")
            return redirect("perfil")
        else:
            messages.error(request, "❌ Por favor corrige los errores.")
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'usuarios/editar_perfil.html', {'form': form})


# ==================== SISTEMA DE ROLES ====================

@login_required
def solicitar_proveedor(request):
    """Solicitud para convertirse en proveedor"""
    perfil = request.user.perfil

    # Validaciones
    if perfil.rol == "proveedor":
        messages.info(request, "ℹ️ Ya eres proveedor.")
        return redirect("perfil")

    # Verificar si ya tiene solicitud pendiente
    solicitud_existente = SolicitudProveedor.objects.filter(
        usuario=request.user,
        estado='pendiente'
    ).exists()

    if solicitud_existente:
        messages.warning(request, "⏳ Ya tienes una solicitud pendiente.")
        return redirect("perfil")

    # Verificar si tiene solicitud rechazada reciente (opcional)
    solicitud_rechazada_reciente = SolicitudProveedor.objects.filter(
        usuario=request.user,
        estado='rechazada',
        fecha_solicitud__gte=timezone.now() - timedelta(days=7)
    ).exists()
    
    if solicitud_rechazada_reciente:
        messages.warning(
            request, 
            "⏰ Tu solicitud fue rechazada recientemente. Puedes volver a intentarlo en 7 días."
        )
        return redirect("perfil")

    # Crear solicitud
    SolicitudProveedor.objects.create(
        usuario=request.user
    )

    messages.success(
        request, 
        "✅ Solicitud enviada correctamente. Recibirás una notificación cuando sea aprobada."
    )
    return redirect("perfil")


# ==================== FUNCIÓN ELIMINADA ====================
# La función 'ser_proveedor' ha sido eliminada porque ahora se usa el flujo de solicitud + aprobación
# Si aún la necesitas, descoméntala aquí:
"""
@login_required
def ser_proveedor(request):
    perfil = request.user.perfil
    perfil.rol = "proveedor"
    perfil.save()
    messages.success(request, "✅ Ahora eres proveedor.")
    return redirect("lista_ofertas")
"""


# ==================== RECUPERACIÓN DE CONTRASEÑA ====================

def password_reset_request(request):
    """Solicitud de recuperación de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Aquí enviarías el email real en producción
            messages.success(
                request, 
                f'📧 Se ha enviado un enlace de recuperación a {email} (modo desarrollo: revisa la consola)'
            )
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, '❌ No existe una cuenta con ese email.')
    
    return render(request, 'usuarios/password_reset.html')