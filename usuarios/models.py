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

    solicitud_proveedor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.rol}"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"