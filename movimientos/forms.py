from django import forms
from .models import Movimiento
from Productos.models import Producto

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['producto', 'tipo', 'cantidad', 'motivo', 'observacion']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'motivo': forms.Select(attrs={'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.all().order_by('nombre')
        self.fields['motivo'].choices = [
            ('', 'Seleccionar motivo...'),
            ('ajuste', 'Ajuste de inventario'),
            ('devolucion', 'Devolución'),
            ('merma', 'Merma / Daño'),
            ('traslado', 'Traslado entre almacenes'),
        ]