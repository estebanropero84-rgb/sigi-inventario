from django import forms
from .models import Categoria, Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'marca', 'modelo', 'categoria', 
                  'stock_actual', 'stock_minimo', 'precio_compra', 
                  'precio_venta', 'ubicacion', 'garantia_meses', 'descripcion']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ELE-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Estante A1'}),
            'garantia_meses': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Electrónicos, Línea Blanca'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la categoría'}),
        }        