from django.contrib import admin
from .models import Oferta, Categoria, Favorito, Comentario, Calificacion


@admin.action(description="Aprobar ofertas seleccionadas")
def aprobar_ofertas(modeladmin, request, queryset):
    queryset.update(estado="activa")


@admin.action(description="Rechazar ofertas seleccionadas")
def rechazar_ofertas(modeladmin, request, queryset):
    queryset.update(estado="rechazada")


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):

    list_display = (
        "titulo",
        "proveedor",
        "precio_descuento",
        "estado",
        "fecha_creacion",
    )

    list_filter = ("estado", "fecha_creacion", "proveedor")

    search_fields = ("titulo", "descripcion")

    actions = [aprobar_ofertas, rechazar_ofertas]

    list_editable = ("estado",)

    ordering = ("-fecha_creacion",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ("nombre",)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "oferta", "fecha_creacion")
    search_fields = ("usuario__username", "oferta__titulo")
    list_filter = ("fecha_creacion",)


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "oferta", "puntuacion")
    list_filter = ("puntuacion",)
    search_fields = ("usuario__username", "oferta__titulo")


admin.site.register(Favorito)