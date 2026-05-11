from django import forms
from .models import Producto, Categoria, Proveedor, Lote, ProductoConSerial, Bodega

# ========== PRODUCTO ==========
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


# ========== CATEGORÍA ==========
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Electrónicos, Línea Blanca'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la categoría'}),
        }


# ========== PROVEEDOR ==========
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'nit', 'telefono', 'email', 'direccion', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ========== LOTE ==========
class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['codigo', 'proveedor', 'fecha_pedido', 'fecha_entrega', 'observaciones']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: LOTE-001'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'fecha_pedido': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ========== BODEGA ==========
class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = ['nombre', 'ubicacion', 'encargado', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'encargado': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }