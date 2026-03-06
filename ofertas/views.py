from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Oferta, Categoria, Favorito, Comentario, Calificacion
from .forms import OfertaForm, ComentarioForm, CalificacionForm
from django.db.models import Avg, Count
from django.contrib.auth.models import User


def lista_ofertas(request):
    ofertas = Oferta.objects.filter(estado="activa")

    buscar = request.GET.get("buscar")
    categoria_id = request.GET.get("categoria")
    orden = request.GET.get("orden")

    if buscar:
        ofertas = ofertas.filter(titulo__icontains=buscar)

    if categoria_id:
        ofertas = ofertas.filter(categorias__id=categoria_id).distinct()

    if orden == "precio_asc":
        ofertas = ofertas.order_by("precio_descuento")
    elif orden == "precio_desc":
        ofertas = ofertas.order_by("-precio_descuento")
    elif orden == "descuento":
        ofertas = ofertas.order_by("-porcentaje_descuento")
    else:
        ofertas = ofertas.order_by("-fecha_creacion")

    paginator = Paginator(ofertas, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.all()

    return render(request, "ofertas/lista.html", {
        "page_obj": page_obj,
        "categorias": categorias,
    })


def detalle_oferta(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)

    if oferta.estado != "activa":
        if not request.user.is_authenticated or request.user.perfil != oferta.proveedor:
            return HttpResponseForbidden("No tienes permiso para ver esta oferta.")

    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(
            usuario=request.user,
            oferta=oferta
        ).exists()

    comentarios = oferta.comentarios.all()

    promedio = oferta.calificaciones.aggregate(Avg("puntuacion"))["puntuacion__avg"]
    total_calificaciones = oferta.calificaciones.count()

    # Calificación usuario actual
    user_calificacion = None
    if request.user.is_authenticated:
        user_calificacion = Calificacion.objects.filter(
            usuario=request.user,
            oferta=oferta
        ).first()

    # Procesar comentario
    if request.method == "POST":
        if "comentario" in request.POST:
            form_comentario = ComentarioForm(request.POST)
            if form_comentario.is_valid():
                comentario = form_comentario.save(commit=False)
                comentario.oferta = oferta
                comentario.usuario = request.user
                comentario.save()
                messages.success(request, "Comentario publicado correctamente.")
                return redirect("detalle_oferta", oferta_id=oferta.id)

        elif "calificacion" in request.POST:
            form_calificacion = CalificacionForm(request.POST)
            if form_calificacion.is_valid():
                calificacion, created = Calificacion.objects.update_or_create(
                    usuario=request.user,
                    oferta=oferta,
                    defaults={"puntuacion": form_calificacion.cleaned_data["puntuacion"]}
                )
                messages.success(request, "Calificación guardada correctamente.")
                return redirect("detalle_oferta", oferta_id=oferta.id)

    else:
        form_comentario = ComentarioForm()
        form_calificacion = CalificacionForm(
            instance=user_calificacion
        )

    return render(request, "ofertas/detalle.html", {
        "oferta": oferta,
        "es_favorito": es_favorito,
        "comentarios": comentarios,
        "form": form_comentario,
        "form_calificacion": form_calificacion,
        "promedio": promedio,
        "total_calificaciones": total_calificaciones
    })


@login_required
def crear_oferta(request):
    if request.user.perfil.rol != "proveedor":
        return HttpResponseForbidden("Solo proveedores pueden crear ofertas.")

    if request.method == "POST":
        # Crear una copia mutable del POST para modificar los precios
        datos_post = request.POST.copy()
        
        # Limpiar los puntos de los precios
        if 'precio_original' in datos_post:
            datos_post['precio_original'] = datos_post['precio_original'].replace('.', '')
        if 'precio_descuento' in datos_post:
            datos_post['precio_descuento'] = datos_post['precio_descuento'].replace('.', '')
        
        form = OfertaForm(datos_post, request.FILES)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.proveedor = request.user.perfil
            oferta.estado = "pendiente"

            # Calcular porcentaje de descuento
            if oferta.precio_original > 0:
                oferta.porcentaje_descuento = (
                    (oferta.precio_original - oferta.precio_descuento)
                    / oferta.precio_original
                ) * 100
            else:
                oferta.porcentaje_descuento = 0

            oferta.save()
            form.save_m2m()

            messages.success(request, "✅ Oferta enviada a revisión correctamente.")
            return redirect("mis_ofertas")
        else:
            messages.error(request, "❌ Error al crear la oferta. Verifica los datos.")
    else:
        form = OfertaForm()

    return render(request, "ofertas/crear.html", {"form": form})

@login_required
def mis_ofertas(request):
    if request.user.perfil.rol != "proveedor":
        return HttpResponseForbidden("Acceso no autorizado.")

    ofertas = Oferta.objects.filter(proveedor=request.user.perfil)

    return render(request, "ofertas/mis_ofertas.html", {
        "ofertas": ofertas
    })


@login_required
def editar_oferta(request, oferta_id):
    if request.user.perfil.rol != "proveedor":
        return HttpResponseForbidden("Acceso no autorizado.")

    oferta = get_object_or_404(
        Oferta,
        id=oferta_id,
        proveedor=request.user.perfil
    )

    # No permitir editar si ya está activa
    if oferta.estado == "activa":
        messages.warning(request, "No puedes editar una oferta ya aprobada.")
        return redirect("mis_ofertas")

    if request.method == "POST":
        form = OfertaForm(request.POST, request.FILES, instance=oferta)
        if form.is_valid():
            oferta = form.save(commit=False)

            if oferta.precio_original > 0:
                oferta.porcentaje_descuento = (
                    (oferta.precio_original - oferta.precio_descuento)
                    / oferta.precio_original
                ) * 100
            else:
                oferta.porcentaje_descuento = 0

            oferta.estado = "pendiente"
            oferta.save()
            form.save_m2m()

            messages.success(request, "Oferta actualizada y enviada nuevamente a revisión.")
            return redirect("mis_ofertas")
        else:
            messages.error(request, "Error al actualizar la oferta.")
    else:
        form = OfertaForm(instance=oferta)

    return render(request, "ofertas/crear.html", {"form": form})


@login_required
def eliminar_oferta(request, oferta_id):
    if request.method != "POST":
        return HttpResponseForbidden("Método no permitido.")

    if request.user.perfil.rol != "proveedor":
        return HttpResponseForbidden("Acceso no autorizado.")

    oferta = get_object_or_404(
        Oferta,
        id=oferta_id,
        proveedor=request.user.perfil
    )

    oferta.delete()
    messages.success(request, "Oferta eliminada correctamente.")

    return redirect("mis_ofertas")


@login_required
def toggle_favorito(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id, estado="activa")

    favorito, creado = Favorito.objects.get_or_create(
        usuario=request.user,
        oferta=oferta
    )

    if not creado:
        favorito.delete()
        messages.info(request, "Oferta eliminada de favoritos.")
    else:
        messages.success(request, "Oferta agregada a favoritos.")

    return redirect("detalle_oferta", oferta_id=oferta.id)


@login_required
def mis_favoritos(request):
    favoritos = Favorito.objects.filter(
        usuario=request.user
    ).select_related("oferta")

    return render(request, "ofertas/mis_favoritos.html", {
        "favoritos": favoritos
    })


@login_required
def dashboard_proveedor(request):
    if request.user.perfil.rol != "proveedor":
        return HttpResponseForbidden("Acceso no autorizado.")

    ofertas = Oferta.objects.filter(proveedor=request.user.perfil)

    total_ofertas = ofertas.count()
    activas = ofertas.filter(estado="activa").count()
    pendientes = ofertas.filter(estado="pendiente").count()
    rechazadas = ofertas.filter(estado="rechazada").count()

    total_favoritos = Favorito.objects.filter(
        oferta__proveedor=request.user.perfil
    ).count()

    total_comentarios = Comentario.objects.filter(
        oferta__proveedor=request.user.perfil
    ).count()

    promedio_general = Calificacion.objects.filter(
        oferta__proveedor=request.user.perfil
    ).aggregate(Avg("puntuacion"))["puntuacion__avg"]

    return render(request, "ofertas/dashboard.html", {
        "total_ofertas": total_ofertas,
        "activas": activas,
        "pendientes": pendientes,
        "rechazadas": rechazadas,
        "total_favoritos": total_favoritos,
        "total_comentarios": total_comentarios,
        "promedio_general": promedio_general
    })


def home(request):
    """Página de inicio con ofertas reales de la base de datos"""
    
    # Ofertas activas ordenadas por fecha - AHORA TRAEMOS 12 OFERTAS
    ofertas = Oferta.objects.filter(estado='activa').order_by('-fecha_creacion')[:12]  # 👈 Cambiado de 8 a 12
    
    # Ofertas destacadas (para el carrusel)
    ofertas_destacadas = Oferta.objects.filter(estado='activa').order_by('-fecha_creacion')[:3]
    
    # Categorías con conteo de ofertas
    categorias = Categoria.objects.annotate(
        total_ofertas=Count('oferta')
    ).filter(total_ofertas__gt=0)[:4]
    
    # Categorías populares (las 5 con más ofertas)
    categorias_populares = Categoria.objects.annotate(
        total_ofertas=Count('oferta')
    ).filter(total_ofertas__gt=0).order_by('-total_ofertas')[:5]
    
    # Estadísticas
    total_ofertas = Oferta.objects.filter(estado='activa').count()
    total_proveedores = User.objects.filter(perfil__rol='proveedor').count()
    
    context = {
        'ofertas': ofertas,
        'ofertas_destacadas': ofertas_destacadas,
        'categorias': categorias,
        'categorias_populares': categorias_populares,
        'total_ofertas': total_ofertas,
        'total_proveedores': total_proveedores,
    }
    
    return render(request, 'home.html', context)


def lista_proveedores(request):
    proveedores = User.objects.filter(perfil__rol='proveedor').order_by('username')
    
    # Buscador
    buscar = request.GET.get('buscar')
    if buscar:
        proveedores = proveedores.filter(
            Q(username__icontains=buscar) | 
            Q(perfil__nombre_completo__icontains=buscar) |
            Q(perfil__sitio_web__icontains=buscar)
        )
    
    # Anotar estadísticas - CORREGIDO: usar perfil para acceder a ofertas
    for proveedor in proveedores:
        # 👇 CORRECCIÓN: proveedor.perfil.ofertas en lugar de proveedor.ofertas
        proveedor.ofertas_activas = Oferta.objects.filter(
            proveedor=proveedor.perfil, 
            estado='activa'
        ).count()
        
        calificaciones = Calificacion.objects.filter(
            oferta__proveedor=proveedor.perfil
        ).aggregate(
            promedio=Avg('puntuacion'),
            total=Count('id')
        )
        proveedor.reputacion = round(calificaciones['promedio'], 1) if calificaciones['promedio'] else None
        proveedor.total_calificaciones = calificaciones['total'] or 0
    
    # Paginación
    paginator = Paginator(proveedores, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'usuarios/proveedores.html', {'proveedores': page_obj})


# ==================== PERFIL PÚBLICO DE PROVEEDOR ====================

def perfil_proveedor(request, username):
    """Perfil público de un proveedor"""
    from django.db.models import Avg, Count
    from django.contrib.auth.models import User
    from ofertas.models import Oferta, Calificacion, Comentario  # 👈 Asegúrate de importar Comentario
    
    proveedor = get_object_or_404(User, username=username)
    
    # Verificar que sea proveedor
    if proveedor.perfil.rol != 'proveedor':
        messages.warning(request, 'Este usuario no es un proveedor.')
        return redirect('lista_proveedores')
    
    # Obtener ofertas activas del proveedor
    ofertas = Oferta.objects.filter(
        proveedor=proveedor.perfil,
        estado='activa'
    ).order_by('-fecha_creacion')
    
    # Calcular reputación
    calificaciones = Calificacion.objects.filter(
        oferta__proveedor=proveedor.perfil
    ).aggregate(
        promedio=Avg('puntuacion'),
        total=Count('id')
    )
    
    # 👇 CORREGIDO: Cambiar 'fecha' por 'fecha_creacion'
    ultimos_comentarios = Comentario.objects.filter(
        oferta__proveedor=proveedor.perfil
    ).order_by('-fecha_creacion')[:5]  # 👈 Cambiado de '-fecha' a '-fecha_creacion'
    
    context = {
        'proveedor': proveedor,
        'perfil': proveedor.perfil,
        'ofertas': ofertas,
        'total_ofertas': ofertas.count(),
        'reputacion': {
            'promedio': round(calificaciones['promedio'], 1) if calificaciones['promedio'] else 0,
            'total': calificaciones['total'] or 0
        },
        'ultimos_comentarios': ultimos_comentarios,
    }
    
    return render(request, 'usuarios/perfil_proveedor.html', context)