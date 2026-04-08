from django import forms
from .models import Compra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor', 'fecha', 'observaciones']
        widgets = {
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }