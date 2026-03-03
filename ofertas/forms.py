from django import forms
from .models import Oferta, Comentario, Calificacion, Categoria

class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ['titulo', 'descripcion', 'precio_original', 'precio_descuento', 'imagen', 'enlace_externo', 'categorias']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control rounded-0', 'placeholder': 'Describe los detalles del producto...'}),
            'enlace_externo': forms.URLInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'https://ejemplo.com/producto'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar campos
        self.fields['titulo'].widget.attrs.update({
            'class': 'form-control rounded-0',
            'placeholder': 'Ej: Portátil HP Pavilion 15.6"'
        })
        
        # 👉 AGREGAR LA CLASE precio-input A LOS CAMPOS DE PRECIO
        self.fields['precio_original'].widget.attrs.update({
            'class': 'form-control rounded-0 precio-input',  # Clase para el JS
            'placeholder': '2.299.900'
        })
        self.fields['precio_descuento'].widget.attrs.update({
            'class': 'form-control rounded-0 precio-input',  # Clase para el JS
            'placeholder': '1.149.900'
        })
        
        # Configurar categorías
        self.fields['categorias'].queryset = Categoria.objects.all()
        self.fields['categorias'].required = True
        self.fields['categorias'].error_messages = {
            'required': 'Debes seleccionar al menos una categoría'
        }
        
        # Hacer enlace_externo opcional
        self.fields['enlace_externo'].required = False
        
        # Formatear valores iniciales si existe instancia
        if self.instance and self.instance.pk:
            if self.instance.precio_original:
                # Formato colombiano para mostrar
                valor = float(self.instance.precio_original)
                self.initial['precio_original'] = f"{valor:,.0f}".replace(',', '.')
            if self.instance.precio_descuento:
                valor = float(self.instance.precio_descuento)
                self.initial['precio_descuento'] = f"{valor:,.0f}".replace(',', '.')
    
    def clean_precio_original(self):
        return self._clean_precio('precio_original')
    
    def clean_precio_descuento(self):
        return self._clean_precio('precio_descuento')
    
    def _clean_precio(self, field_name):
        precio = self.cleaned_data.get(field_name)
        
        # Si es string, limpiarlo (quitar puntos, convertir comas a puntos)
        if isinstance(precio, str):
            # Eliminar puntos de miles
            precio_limpio = precio.replace('.', '')
            # Reemplazar coma por punto si existe
            precio_limpio = precio_limpio.replace(',', '.')
            
            try:
                precio = float(precio_limpio)
            except ValueError:
                raise forms.ValidationError("Ingresa un valor numérico válido")
        
        if precio is None:
            raise forms.ValidationError("Este campo es requerido")
        
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a cero")
        
        # Redondear a 2 decimales
        return round(precio, 2)
    
    def clean(self):
        cleaned_data = super().clean()
        precio_original = cleaned_data.get('precio_original')
        precio_descuento = cleaned_data.get('precio_descuento')
        
        if precio_original and precio_descuento:
            if precio_descuento >= precio_original:
                raise forms.ValidationError("El precio con descuento debe ser menor al precio original")
        
        return cleaned_data


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["contenido"]
        widgets = {
            "contenido": forms.Textarea(attrs={
                "class": "form-control rounded-0",
                "rows": 3,
                "placeholder": "Escribe tu comentario..."
            })
        }


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ["puntuacion"]
        widgets = {
            "puntuacion": forms.Select(
                choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={"class": "form-select rounded-0"}
            )
        }