from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil
import re

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # 1. Validar que no esté duplicado
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("❌ Este email ya está registrado")
        
        # 2. Validar formato básico (cualquier dominio)
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron_email, email):
            raise forms.ValidationError("❌ El formato del email no es válido")
        
        # 3. Validar que el dominio tenga al menos un punto (ej: gmail.com, empresa.com.co)
        dominio = email.split('@')[1]
        if '.' not in dominio:
            raise forms.ValidationError("❌ El dominio del email no es válido")
        
        # ✅ ACEPTA CUALQUIER DOMINIO CON FORMATO VÁLIDO
        # Gmail, Hotmail, Yahoo, empresas colombianas (vecol.com.co), etc.
        
        return email.lower()  # Guardar en minúsculas
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Validar que el username no exista
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("❌ Este nombre de usuario ya está en uso")
        
        # Validar longitud y caracteres
        if len(username) < 3:
            raise forms.ValidationError("❌ El nombre de usuario debe tener al menos 3 caracteres")
        
        if len(username) > 150:
            raise forms.ValidationError("❌ El nombre de usuario no puede tener más de 150 caracteres")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("❌ Solo letras, números y guión bajo")
        
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("❌ Las contraseñas no coinciden")
        
        # Validaciones de contraseña
        if len(password1) < 8:
            raise forms.ValidationError("❌ La contraseña debe tener al menos 8 caracteres")
        
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError("❌ La contraseña debe tener al menos un número")
        
        if not any(char.isalpha() for char in password1):
            raise forms.ValidationError("❌ La contraseña debe tener al menos una letra")
        
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
            # Crear perfil automáticamente (si no se crea con señal)
            Perfil.objects.get_or_create(user=user)
            
        return user

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefono', 'direccion', 'foto', 'descripcion']