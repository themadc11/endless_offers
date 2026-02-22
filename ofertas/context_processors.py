def favoritos_count(request):
    if request.user.is_authenticated:
        from .models import Favorito
        return {
            "favoritos_count": Favorito.objects.filter(
                usuario=request.user
            ).count()
        }
    return {"favoritos_count": 0}