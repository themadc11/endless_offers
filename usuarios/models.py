from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):

    ROLES = (
        ('consumidor', 'Consumidor'),
        ('proveedor', 'Proveedor'),
    )
    
    NIVELES = (
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
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
    nombre_completo = models.CharField(max_length=100, blank=True)
    
    # Sitio web oficial (solo para proveedores)
    sitio_web = models.URLField(max_length=200, blank=True, null=True, verbose_name="Sitio web oficial")
    
    # 👇 NUEVO: Nivel de verificación (reemplaza al booleano 'verificado')
    nivel_verificacion = models.CharField(
        max_length=20, 
        choices=NIVELES, 
        default='basico',
        verbose_name="Nivel de verificación"
    )
    
    # Mantenemos 'verificado' por compatibilidad (opcional)
    verificado = models.BooleanField(default=False)

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

    NIVELES = (
        ('basico', 'Verificación Básica'),
        ('intermedio', 'Verificación Intermedia'),
        ('avanzado', 'Verificación Avanzada'),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    nivel_solicitado = models.CharField(max_length=20, choices=NIVELES, default='basico')
    
    # Información BÁSICA (obligatoria para todos)
    telefono_contacto = models.CharField(max_length=20, verbose_name="Teléfono de contacto")
    descripcion_negocio = models.TextField(verbose_name="¿Qué productos o servicios ofreces?")
    
    # Información INTERMEDIA (opcional)
    sitio_web = models.URLField(max_length=200, blank=True, verbose_name="Sitio web o red social")
    instagram = models.CharField(max_length=100, blank=True, verbose_name="Instagram")
    facebook = models.CharField(max_length=100, blank=True, verbose_name="Facebook")
    fotos_productos = models.FileField(upload_to='productos_proveedores/', blank=True, null=True)
    
    # Información AVANZADA (para mayor confianza)
    experiencia = models.TextField(blank=True, verbose_name="Experiencia en ventas")
    documentos = models.FileField(upload_to='documentos_proveedores/', blank=True, null=True)
    referencias = models.TextField(blank=True, verbose_name="Referencias comerciales")
    
    # Evaluación del admin
    nivel_asignado = models.CharField(max_length=20, choices=NIVELES, default='basico')
    notas_admin = models.TextField(blank=True, verbose_name="Notas del administrador")
    fecha_revision = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_nivel_solicitado_display()}"

    class Meta:
        verbose_name = "Solicitud de Proveedor"
        verbose_name_plural = "Solicitudes de Proveedor"