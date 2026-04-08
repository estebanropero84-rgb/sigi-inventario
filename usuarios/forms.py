from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirmar contraseña')
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'telefono', 'direccion', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned_data