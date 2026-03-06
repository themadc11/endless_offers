from django.db.models import Count
from .models import Categoria

def favoritos_count(request):
    if request.user.is_authenticated:
        from .models import Favorito
        return {
            "favoritos_count": Favorito.objects.filter(
                usuario=request.user
            ).count()
        }
    return {"favoritos_count": 0}

def categorias_menu(request):
    """Devuelve las categorías para el menú desplegable"""
    categorias = Categoria.objects.annotate(
        total_ofertas=Count('oferta')
    ).filter(total_ofertas__gt=0).order_by('nombre')
    
    return {
        'categorias_menu': categorias
    }