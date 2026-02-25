from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy


from .forms import RegistroForm, PerfilForm
from .models import SolicitudProveedor

# ==================== AUTENTICACIÓN ====================

def login_view(request):
    """Vista personalizada de inicio de sesión que acepta email o username"""
    if request.user.is_authenticated:
        return redirect('lista_ofertas')
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Verificar si es email o username
        user = None
        if '@' in username_or_email:
            # Es un email - buscar usuario por email
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            # Es username - autenticar directamente
            user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('lista_ofertas')
        else:
            messages.error(request, '❌ Usuario/Email o contraseña incorrectos')
            return redirect('login')
    
    return render(request, 'usuarios/login.html')


def registro(request):
    """Registro de nuevo usuario con login automático"""
    if request.user.is_authenticated:
        return redirect('lista_ofertas')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el usuario
            
            # 👇 LOGIN AUTOMÁTICO
            login(request, user)
            
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('lista_ofertas')  # Redirige al home
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

# VERSIÓN CORREGIDA - Usando la clase de Django
class CustomPasswordResetView(PasswordResetView):
    template_name = 'usuarios/password_reset.html'
    email_template_name = 'usuarios/password_reset_email.html'
    subject_template_name = 'usuarios/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    html_email_template_name = 'usuarios/password_reset_email.html'  # 👈 ESTA LÍNEA ES CLAVE
    
    def form_valid(self, form):
        messages.success(self.request, '📧 Revisa tu correo. Te hemos enviado las instrucciones.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        email = self.request.POST.get('email', '')
        messages.error(self.request, f'❌ No encontramos una cuenta con el email: {email}')
        return super().form_invalid(form)

# Si quieres mantener tu función simple, así debe quedar:
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Verificar si existe el email
            if User.objects.filter(email=email).exists():
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name='usuarios/password_reset_email.html'
                )
                messages.success(request, f'📧 Hemos enviado instrucciones a {email}')
                return redirect('password_reset_done')
            else:
                messages.error(request, f'❌ No existe una cuenta con ese email')
    else:
        form = PasswordResetForm()
    
    return render(request, 'usuarios/password_reset.html', {'form': form})