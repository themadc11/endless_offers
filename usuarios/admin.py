from django.contrib import admin
from .models import Perfil, SolicitudProveedor


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "telefono")


@admin.register(SolicitudProveedor)
class SolicitudProveedorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "estado", "fecha_solicitud")
    list_filter = ("estado",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Si se aprueba → cambiar rol
        if obj.estado == "aprobada":
            perfil = obj.usuario.perfil
            perfil.rol = "proveedor"
            perfil.save()