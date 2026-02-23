from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):

    ROLES = (
        ('consumidor', 'Consumidor'),
        ('proveedor', 'Proveedor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='consumidor'
    )

    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.rol}"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"


class SolicitudProveedor(models.Model):

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    mensaje = models.TextField(blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.estado}"

    class Meta:
        verbose_name = "Solicitud de Proveedor"
        verbose_name_plural = "Solicitudes de Proveedor"