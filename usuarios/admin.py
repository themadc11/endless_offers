from django.contrib import admin
from .models import Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "solicitud_proveedor")
    list_filter = ("rol", "solicitud_proveedor")
