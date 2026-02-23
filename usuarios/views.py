from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm
from django.contrib import messages
from .models import SolicitudProveedor
from .forms import PerfilForm

def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("lista_ofertas")
    else:
        form = UserCreationForm()

    return render(request, "usuarios/registro.html", {"form": form})

@login_required
def ser_proveedor(request):
    perfil = request.user.perfil
    perfil.rol = "proveedor"
    perfil.save()
    return redirect("lista_ofertas")


def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # inicia sesión automáticamente
            return redirect("lista_ofertas")
    else:
        form = RegistroForm()

    return render(request, "usuarios/registro.html", {"form": form})



@login_required
def solicitar_proveedor(request):

    # Verificar si ya tiene solicitud pendiente
    existe = SolicitudProveedor.objects.filter(
        usuario=request.user,
        estado='pendiente'
    ).exists()

    if existe:
        messages.warning(request, "Ya tienes una solicitud pendiente.")
        return redirect("perfil")

    SolicitudProveedor.objects.create(
        usuario=request.user
    )

    messages.success(request, "Solicitud enviada correctamente.")
    return redirect("perfil")

@login_required
def perfil(request):
    perfil = request.user.perfil

    return render(request, "usuarios/perfil.html", {
        "perfil": perfil
    })

@login_required
def editar_perfil(request):

    perfil = request.user.perfil

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil")
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'usuarios/editar_perfil.html', {'form': form})
