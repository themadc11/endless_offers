from django.apps import AppConfig

class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificaciones'
    
    def ready(self):
        # Esto es CRUCIAL para que las señales se carguen
        import notificaciones.signals