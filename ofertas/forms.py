from django import forms
from .models import Oferta, Comentario, Calificacion

class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        exclude = ["proveedor", "estado", "porcentaje_descuento"]

    def clean(self):
        cleaned_data = super().clean()
        precio_original = cleaned_data.get("precio_original")
        precio_descuento = cleaned_data.get("precio_descuento")

        if precio_original and precio_descuento:
            if precio_descuento > precio_original:
                raise forms.ValidationError(
                    "El precio con descuento no puede ser mayor que el precio original."
                )

        return cleaned_data
    

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["contenido"]
        widgets = {
            "contenido": forms.Textarea(attrs={
                "class": "form-control",
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
                attrs={"class": "form-select"}
            )
        }