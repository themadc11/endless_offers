from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm
from django.contrib import messages


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
    perfil = request.user.perfil

    if perfil.rol == "proveedor":
        messages.warning(request, "Ya eres proveedor.")
        return redirect("perfil")

    perfil.solicitud_proveedor = True
    perfil.save()

    messages.success(request, "Tu solicitud para ser proveedor fue enviada al administrador.")
    return redirect("perfil")
