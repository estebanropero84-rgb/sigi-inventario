from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from decimal import Decimal
from .models import Producto, Categoria, Proveedor, Lote, ProductoConSerial, Bodega, Ubicacion, Movimiento
import re


# ========== UBICACIÓN ==========
class UbicacionForm(forms.ModelForm):
    """Formulario para gestionar ubicaciones predefinidas"""
    
    class Meta:
        model = Ubicacion
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Estante A1, Bodega Principal, Pasillo 3'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada de la ubicación...'
            }),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            if Ubicacion.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Ya existe una ubicación con este nombre')
        return nombre


# ========== PRODUCTO CON VALIDACIONES COMPLETAS ==========
class ProductoForm(forms.ModelForm):
    codigo = forms.CharField(
        max_length=50,
        required=True,
        label='Código',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ej: ELE-001',
            'autofocus': True
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un código válido.'
        },
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\-_]{3,50}$',
                message='El código debe tener entre 3 y 50 caracteres, solo letras, números, guiones y guiones bajos'
            )
        ]
    )
    
    # 🔥 CÓDIGO DE BARRAS - REALMENTE OPCIONAL
    codigo_barras = forms.CharField(
        max_length=100,
        required=False,  # 🔥 OPCIONAL
        label='Código de barras',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Opcional'
        }),
        error_messages={
            'invalid': 'Ingresa un código de barras válido.'
        },
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\-_]{0,100}$',
                message='El código de barras solo puede contener letras, números, guiones y guiones bajos'
            )
        ]
    )
    
    nombre = forms.CharField(
        max_length=200,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del producto'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    
    marca = forms.CharField(
        max_length=100,
        required=True,
        label='Marca',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Samsung, LG, Whirlpool'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    
    modelo = forms.CharField(
        max_length=100,
        required=True,
        label='Modelo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: XJ-1000, Inverter Plus'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    
    stock_minimo = forms.IntegerField(
        required=True,
        label='Stock mínimo',
        validators=[
            MinValueValidator(0, message='El stock mínimo no puede ser negativo')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'placeholder': '5'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un número válido.'
        }
    )
    
    precio_compra = forms.DecimalField(
        required=True,
        label='Precio compra',
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'), message='El precio de compra debe ser mayor a 0')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un valor numérico válido.'
        }
    )
    
    precio_venta = forms.DecimalField(
        required=True,
        label='Precio venta',
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'), message='El precio de venta debe ser mayor a 0')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un valor numérico válido.'
        }
    )
    
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all().order_by('nombre'),
        required=False,
        label='Categoría',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    ubicacion = forms.ModelChoiceField(
        queryset=Ubicacion.objects.all().order_by('nombre'),
        required=False,
        label='Ubicación',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    garantia_meses = forms.IntegerField(
        required=False,
        label='Garantía (meses)',
        validators=[
            MinValueValidator(0, message='La garantía no puede ser negativa')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'placeholder': '12'
        })
    )
    
    descripcion = forms.CharField(
        required=False,
        label='Descripción',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descripción detallada del producto...'
        })
    )
    
    class Meta:
        model = Producto
        fields = ['codigo', 'codigo_barras', 'nombre', 'marca', 'modelo', 'categoria', 
                  'stock_minimo', 'precio_compra', 'precio_venta', 'ubicacion', 
                  'garantia_meses', 'descripcion']
        widgets = {
            'bodega': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🔥 Asegurar que el código de barras sea opcional
        self.fields['codigo_barras'].required = False
        self.fields['codigo_barras'].help_text = 'ℹ️ Opcional - Déjalo vacío si no tiene código de barras'
        
        for field_name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
    
    # ====== VALIDACIONES MEJORADAS ======
    
    def clean_codigo(self):
        """Validación robusta del código"""
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            if not re.match(r'^[A-Za-z0-9\-_]{3,50}$', codigo):
                raise ValidationError('El código debe tener entre 3 y 50 caracteres, solo letras, números, guiones y guiones bajos.')
            
            if Producto.objects.filter(codigo=codigo).exists():
                if self.instance and self.instance.pk:
                    if Producto.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
                        raise ValidationError(f'El código "{codigo}" ya está en uso por otro producto.')
                else:
                    raise ValidationError(f'El código "{codigo}" ya está en uso.')
        return codigo
    
    def clean_nombre(self):
        """Validación del nombre"""
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            if len(nombre) < 3:
                raise ValidationError('El nombre debe tener al menos 3 caracteres.')
            if len(nombre) > 200:
                raise ValidationError('El nombre no puede tener más de 200 caracteres.')
        return nombre
    
    def clean_marca(self):
        """Validación de la marca"""
        marca = self.cleaned_data.get('marca')
        if marca:
            if len(marca) < 2:
                raise ValidationError('La marca debe tener al menos 2 caracteres.')
        return marca
    
    def clean_modelo(self):
        """Validación del modelo"""
        modelo = self.cleaned_data.get('modelo')
        if modelo:
            if len(modelo) < 2:
                raise ValidationError('El modelo debe tener al menos 2 caracteres.')
        return modelo
    
    def clean_precio_compra(self):
        """Validación del precio de compra"""
        precio = self.cleaned_data.get('precio_compra')
        if precio is not None:
            if precio < 0:
                raise ValidationError('El precio de compra no puede ser negativo.')
            if precio > 999999999:
                raise ValidationError('El precio de compra no puede ser mayor a 999,999,999.')
        return precio
    
    def clean_precio_venta(self):
        """Validación del precio de venta"""
        precio = self.cleaned_data.get('precio_venta')
        if precio is not None:
            if precio <= 0:
                raise ValidationError('El precio de venta debe ser mayor a 0.')
            if precio > 999999999:
                raise ValidationError('El precio de venta no puede ser mayor a 999,999,999.')
        return precio
    
    def clean_stock_minimo(self):
        """Validación del stock mínimo"""
        stock = self.cleaned_data.get('stock_minimo')
        if stock is not None:
            if stock < 0:
                raise ValidationError('El stock mínimo no puede ser negativo.')
            if stock > 999999:
                raise ValidationError('El stock mínimo no puede ser mayor a 999,999.')
        return stock
    
    def clean(self):
        """Validaciones cruzadas entre campos"""
        cleaned_data = super().clean()
        precio_compra = cleaned_data.get('precio_compra')
        precio_venta = cleaned_data.get('precio_venta')
        
        # Validar que precio_venta > precio_compra
        if precio_compra is not None and precio_venta is not None:
            if precio_venta <= precio_compra:
                raise ValidationError({
                    'precio_venta': f'El precio de venta (${precio_venta:,.2f}) debe ser mayor que el precio de compra (${precio_compra:,.2f}).'
                })
        
        # Validar margen mínimo de ganancia (10%) usando Decimal
        if precio_compra is not None and precio_venta is not None:
            margen = precio_venta - precio_compra
            margen_minimo = precio_compra * Decimal('0.1')
            if margen < margen_minimo:
                raise ValidationError({
                    'precio_venta': f'El margen de ganancia (${margen:,.2f}) debe ser al menos el 10% del precio de compra (${margen_minimo:,.2f}).'
                })
        
        return cleaned_data
    
    def clean_codigo_barras(self):
        """Validación del código de barras - OPCIONAL"""
        codigo_barras = self.cleaned_data.get('codigo_barras')
        
        # 🔥 Si está vacío, permitir sin validación
        if not codigo_barras:
            return codigo_barras
        
        # Si tiene valor, validar formato
        if not re.match(r'^[A-Za-z0-9\-_]{0,100}$', codigo_barras):
            raise ValidationError('El código de barras solo puede contener letras, números, guiones y guiones bajos.')
        
        # Validar unicidad solo si tiene valor
        instance = self.instance
        if instance and instance.pk:
            producto_existente = Producto.objects.filter(
                codigo_barras=codigo_barras
            ).exclude(pk=instance.pk).first()
            if producto_existente:
                raise ValidationError(
                    f'⚠️ El código de barras "{codigo_barras}" ya está registrado en el producto "{producto_existente.nombre}".'
                )
        else:
            producto_existente = Producto.objects.filter(codigo_barras=codigo_barras).first()
            if producto_existente:
                raise ValidationError(
                    f'⚠️ El código de barras "{codigo_barras}" ya está registrado en el producto "{producto_existente.nombre}".'
                )
        
        return codigo_barras


# ========== CATEGORÍA ==========
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Electrónicos, Línea Blanca'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la categoría'}),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Ya existe una categoría con este nombre')
        return nombre


# ========== PROVEEDOR ==========
class ProveedorForm(forms.ModelForm):
    nit = forms.CharField(
        max_length=20,
        required=True,
        label='NIT',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 123456789-0'}),
        error_messages={
            'required': 'Este campo es obligatorio.'
        },
        validators=[
            RegexValidator(
                regex=r'^[0-9\-]+$',
                message='El NIT solo puede contener números y guiones'
            )
        ]
    )
    
    telefono = forms.CharField(
        max_length=20,
        required=True,
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3001234567'}),
        error_messages={
            'required': 'Este campo es obligatorio.'
        },
        validators=[
            RegexValidator(
                regex=r'^[0-9\-+]+$',
                message='El teléfono solo puede contener números, guiones y +'
            )
        ]
    )
    
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'proveedor@email.com'}),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un correo electrónico válido.'
        }
    )
    
    class Meta:
        model = Proveedor
        fields = ['nombre', 'nit', 'telefono', 'email', 'direccion', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección del proveedor'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del contacto'}),
        }
    
    def clean_nit(self):
        nit = self.cleaned_data.get('nit')
        if nit:
            if Proveedor.objects.filter(nit=nit).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este NIT ya está registrado')
        return nit


# ========== BODEGA ==========
class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = ['nombre', 'ubicacion', 'encargado', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la bodega'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación'}),
            'encargado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del encargado'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono de contacto'}),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            if Bodega.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Ya existe una bodega con este nombre')
        return nombre


# ========== LOTE COMPLETO ==========
class LoteCompletoForm(forms.ModelForm):
    codigo = forms.CharField(
        max_length=50,
        required=True,
        label='Código',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: LOTE-001'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.'
        },
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\-_]+$',
                message='El código solo puede contener letras, números, guiones y guiones bajos'
            )
        ]
    )
    
    cantidad_total = forms.IntegerField(
        required=True,
        label='Cantidad total',
        validators=[
            MinValueValidator(1, message='La cantidad debe ser mayor a 0')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'Cantidad total del lote'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un número válido.'
        }
    )
    
    costo_unitario = forms.DecimalField(
        required=True,
        label='Costo unitario',
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'), message='El costo unitario debe ser mayor a 0')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un valor numérico válido.'
        }
    )
    
    class Meta:
        model = Lote
        fields = ['codigo', 'producto', 'proveedor', 'cantidad_total', 
                  'costo_unitario', 'fecha_estimada', 'observaciones']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'fecha_estimada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones del lote'}),
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            if Lote.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
                raise ValidationError(f'El código "{codigo}" ya está en uso')
        return codigo


# ========== RECEPCIÓN DE LOTE ==========
class RecepcionLoteForm(forms.Form):
    cantidad = forms.IntegerField(
        min_value=1,
        label='Cantidad',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cantidad a recibir',
            'min': '1'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un número válido.',
            'min_value': 'La cantidad debe ser mayor a 0.'
        }
    )
    
    seriales = forms.CharField(
        label='Seriales',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'SN-001\nSN-002\nSN-003\nSN-004\n(Un serial por línea)'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    
    notas = forms.CharField(
        required=False,
        label='Notas',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Notas adicionales (opcional)'
        })
    )
    
    def clean_seriales(self):
        seriales_text = self.cleaned_data.get('seriales', '')
        if not seriales_text.strip():
            raise ValidationError('Debes ingresar al menos un serial')
        
        seriales_lista = [s.strip() for s in seriales_text.strip().split('\n') if s.strip()]
        
        if len(seriales_lista) != len(set(seriales_lista)):
            raise ValidationError('Hay seriales duplicados en la lista')
        
        for serial in seriales_lista:
            if not re.match(r'^[A-Za-z0-9\-_]{3,50}$', serial):
                raise ValidationError(f'El serial "{serial}" tiene formato inválido (solo letras, números, guiones, mínimo 3 caracteres)')
        
        return seriales_text


# ========== SERIAL ==========
class SerialForm(forms.ModelForm):
    serial = forms.CharField(
        max_length=50,
        required=True,
        label='Serial',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: SN-2024-001'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.'
        },
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\-_]{5,50}$',
                message='El serial solo puede contener letras, números, guiones y guiones bajos (mínimo 5 caracteres)'
            )
        ]
    )
    
    class Meta:
        model = ProductoConSerial
        fields = ['serial', 'estado', 'notas']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas sobre este serial...'}),
        }
    
    def clean_serial(self):
        serial = self.cleaned_data.get('serial')
        if serial:
            if ProductoConSerial.objects.filter(serial=serial).exclude(pk=self.instance.pk).exists():
                raise ValidationError(f'El serial "{serial}" ya está registrado')
        return serial


# ========== BUSCAR SERIAL ==========
class BuscarSerialForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por serial...'})
    )
    estado = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[('', 'Todos los estados')] + list(ProductoConSerial.ESTADOS_SERIAL),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    producto = forms.ModelChoiceField(
        required=False,
        label='Producto',
        queryset=Producto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# ========== MOVIMIENTO ==========
class MovimientoForm(forms.ModelForm):
    """Formulario para registrar movimientos con selección de producto y lote"""
    
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'),
        required=True,
        label='Producto',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_producto'
        })
    )
    
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.all().order_by('-created_at'),
        required=False,
        label='Lote (opcional)',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_lote'
        })
    )
    
    class Meta:
        model = Movimiento
        fields = ['producto', 'lote', 'tipo', 'cantidad', 'descripcion']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_tipo'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Cantidad'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del movimiento...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lote'].queryset = Lote.objects.filter(
            cantidad_recibida__gt=models.F('cantidad_vendida')
        ).order_by('-created_at')
        
        if 'producto' in self.data:
            try:
                producto_id = int(self.data.get('producto'))
                self.fields['lote'].queryset = Lote.objects.filter(
                    producto_id=producto_id,
                    cantidad_recibida__gt=models.F('cantidad_vendida')
                ).order_by('-created_at')
            except (ValueError, TypeError):
                pass
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a 0')
        return cantidad
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        lote = cleaned_data.get('lote')
        
        if producto and lote and lote.producto != producto:
            raise ValidationError({
                'lote': f'El lote seleccionado ({lote.codigo}) no pertenece al producto {producto.nombre}.'
            })
        
        return cleaned_data