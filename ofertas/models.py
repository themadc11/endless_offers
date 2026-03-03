from django.db import models
from usuarios.models import Perfil
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


class Oferta(models.Model):

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('activa', 'Activa'),
        ('rechazada', 'Rechazada'),
    )

    proveedor = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'proveedor'}
    )

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # 👉 DecimalField con 15 dígitos totales y 2 decimales (suficiente para cualquier oferta)
    precio_original = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Precio original")
    precio_descuento = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Precio con descuento")
    
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    imagen = models.ImageField(upload_to='ofertas/', blank=True, null=True)
    enlace_externo = models.URLField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    categorias = models.ManyToManyField(Categoria)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"


class Favorito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "oferta")

    def __str__(self):
        return f"{self.usuario} ❤️ {self.oferta}"
    
class Comentario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='comentarios')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.oferta.titulo}"
    

class Calificacion(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name="calificaciones")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()

    fecha_creacion = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["oferta", "usuario"], name="unique_calificacion")
        ]

    def __str__(self):
        return f"{self.usuario.username} calificó {self.oferta.titulo} con {self.puntuacion}"