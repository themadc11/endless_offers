from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notificacion(models.Model):
    TIPOS = (
        ('solicitud_proveedor', 'Solicitud de Proveedor'),
        ('aprobacion_proveedor', 'Aprobación de Proveedor'),
        ('rechazo_proveedor', 'Rechazo de Proveedor'),
        ('nueva_oferta', 'Nueva Oferta'),
        ('aprobacion_oferta', 'Aprobación de Oferta'),
        ('rechazo_oferta', 'Rechazo de Oferta'),
        ('nuevo_comentario', 'Nuevo Comentario'),
        ('nueva_calificacion', 'Nueva Calificación'),
        ('nuevo_favorito', 'Nuevo Favorito'),
        ('sistema', 'Notificación del Sistema'),
    )
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=30, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)  # URL a donde llevar al hacer click
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"