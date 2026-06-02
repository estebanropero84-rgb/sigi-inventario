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


# ========== LOTE COMPLETO (CREAR LOTE) ==========
class LoteCompletoForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['codigo', 'producto', 'proveedor', 'cantidad_total', 
                  'costo_unitario', 'fecha_estimada', 'observaciones']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: LOTE-001'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_total': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Cantidad total del lote'}),
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Costo por unidad'}),
            'fecha_estimada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones del lote'}),
        }


# ========== RECEPCIÓN DE LOTE (RECIBIR CON SERIALES) ==========
class RecepcionLoteForm(forms.Form):
    """Formulario para recibir productos de un lote con seriales"""
    cantidad = forms.IntegerField(
        min_value=1, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad a recibir'})
    )
    seriales = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 6,
            'placeholder': 'SN-001\nSN-002\nSN-003\nSN-004\n(Un serial por línea)'
        }),
        help_text="Ingresa los seriales, uno por línea. La cantidad debe coincidir con el número de seriales."
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas adicionales (opcional)'})
    )


# ========== SERIAL (EDITAR ESTADO) ==========
class SerialForm(forms.ModelForm):
    class Meta:
        model = ProductoConSerial
        fields = ['estado', 'notas']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas sobre este serial...'}),
        }


# ========== BUSCAR SERIAL ==========
class BuscarSerialForm(forms.Form):
    """Formulario para buscar seriales"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por serial...'})
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + list(ProductoConSerial.ESTADOS_SERIAL),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    producto = forms.ModelChoiceField(
        required=False,
        queryset=Producto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )