from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout  # 👈 Agregado logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

from .forms import RegistroForm, PerfilForm
from .models import Perfil, SolicitudProveedor

# ==================== AUTENTICACIÓN ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    error_message = None
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username_or_email or not password:
            error_message = '❌ Por favor ingresa usuario/email y contraseña'
        else:
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    error_message = '❌ No existe una cuenta con ese email'
            else:
                user = authenticate(request, username=username_or_email, password=password)
                if not user:
                    error_message = '❌ Usuario/Email o contraseña incorrectos'
            
            if user:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.username}!')
                return redirect('home')
        
        return render(request, 'usuarios/login.html', {'error': error_message})
    
    return render(request, 'usuarios/login.html')


def logout_view(request):
    """Cerrar sesión y redirigir al home"""
    logout(request)
    return redirect('home')


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


# ==================== PERFIL ====================

@login_required
def perfil(request):
    """Vista del perfil del usuario"""
    # Crear perfil si no existe
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, "Perfil creado automáticamente. Completa tus datos.")
    
    solicitud = SolicitudProveedor.objects.filter(
        usuario=request.user
    ).order_by('-fecha_solicitud').first()
    
    context = {
        "perfil": perfil,
        "solicitud": solicitud,
    }
    
    # Si es proveedor, obtenemos datos extra
    if perfil.rol == 'proveedor':
        from ofertas.models import Oferta, Calificacion
        
        ofertas_activas = Oferta.objects.filter(
            proveedor=perfil,
            estado='activa'
        ).count()
        
        calificaciones = Calificacion.objects.filter(
            oferta__proveedor=perfil
        ).aggregate(
            promedio=Avg('puntuacion'),
            total=Count('id')
        )
        
        context.update({
            "ofertas_activas": ofertas_activas,
            "reputacion": {
                'promedio': round(calificaciones['promedio'], 1) if calificaciones['promedio'] else 0,
                'total': calificaciones['total'] or 0
            }
        })
    
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

    # 👇 PASAMOS LA INSTANCIA perfil Y LA VARIABLE es_proveedor
    context = {
        'form': form,
        'perfil': perfil,  # 👈 ESTO ES LO QUE FALTABA
        'es_proveedor': perfil.rol == 'proveedor',
    }
    
    return render(request, 'usuarios/editar_perfil.html', context)


# ==================== SISTEMA DE ROLES ====================

@login_required
def solicitar_proveedor(request):
    """Solicitud para convertirse en proveedor"""
    perfil = request.user.perfil

    if perfil.rol == "proveedor":
        messages.info(request, "ℹ️ Ya eres proveedor.")
        return redirect("perfil")

    # Verificar solicitud pendiente
    solicitud_existente = SolicitudProveedor.objects.filter(
        usuario=request.user,
        estado='pendiente'
    ).exists()

    if solicitud_existente:
        messages.warning(request, "⏳ Ya tienes una solicitud pendiente.")
        return redirect("perfil")

    if request.method == 'POST':
        # Crear solicitud con toda la información
        solicitud = SolicitudProveedor.objects.create(
            usuario=request.user,
            nivel_solicitado=request.POST.get('nivel_solicitado', 'basico'),
            telefono_contacto=request.POST.get('telefono_contacto', ''),
            descripcion_negocio=request.POST.get('descripcion_negocio', ''),
            sitio_web=request.POST.get('sitio_web', ''),
            instagram=request.POST.get('instagram', ''),
            facebook=request.POST.get('facebook', ''),
            fotos_productos=request.FILES.get('fotos_productos'),
            experiencia=request.POST.get('experiencia', ''),
            documentos=request.FILES.get('documentos'),
            referencias=request.POST.get('referencias', ''),
            estado='pendiente'
        )
        
        messages.success(request, "✅ Solicitud enviada correctamente. Revisaremos tu información.")
        return redirect("perfil")
    
    return render(request, "usuarios/solicitar_proveedor.html")


# ==================== RECUPERACIÓN DE CONTRASEÑA ====================
class CustomPasswordResetView(PasswordResetView):
    template_name = 'usuarios/password_reset.html'
    email_template_name = 'usuarios/password_reset_email.html'
    subject_template_name = 'usuarios/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    html_email_template_name = 'usuarios/password_reset_email.html'
    
    def form_valid(self, form):
        messages.success(self.request, '📧 Revisa tu correo. Te hemos enviado las instrucciones.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        email = self.request.POST.get('email', '')
        messages.error(self.request, f'❌ No encontramos una cuenta con el email: {email}')
        return super().form_invalid(form)
    
    
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
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