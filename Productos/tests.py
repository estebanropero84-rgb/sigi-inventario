from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from .models import Producto, Categoria, Proveedor, Bodega, Lote, ProductoConSerial

Usuario = get_user_model()


class ProductoTestCase(TestCase):
    """Pruebas unitarias para el sistema de inventario SIGI"""
    
    def setUp(self):
        """Configuración inicial - se ejecuta antes de cada prueba"""
        # Crear usuario de prueba
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            rol='admin'
        )
        
        # Crear categoría de prueba
        self.categoria = Categoria.objects.create(
            nombre='Electrodomésticos',
            descripcion='Productos del hogar'
        )
        
        # Crear bodega de prueba
        self.bodega = Bodega.objects.create(
            nombre='Bodega Principal',
            ubicacion='Calle 123'
        )
        
        # Crear proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nombre='LG Electronics',
            nit='900123456-1',
            telefono='1234567'
        )
    
    # ========== PRUEBAS DE PRODUCTOS ==========
    
    def test_01_crear_producto(self):
        """Prueba: Crear un producto correctamente"""
        producto = Producto.objects.create(
            codigo='TEST-001',
            nombre='Lavadora LG',
            marca='LG',
            categoria=self.categoria,
            bodega=self.bodega,
            stock_actual=10,
            stock_minimo=3,
            precio_venta=850.00
        )
        
        self.assertEqual(producto.nombre, 'Lavadora LG')
        self.assertEqual(producto.codigo, 'TEST-001')
        self.assertEqual(producto.stock_actual, 10)
        self.assertEqual(producto.precio_venta, 850.00)
    
    def test_02_actualizar_stock(self):
        """Prueba: Actualizar el stock de un producto"""
        producto = Producto.objects.create(
            codigo='TEST-002',
            nombre='Refrigerador Samsung',
            stock_actual=5,
            precio_venta=1200.00
        )
        
        producto.stock_actual = 8
        producto.save()
        
        self.assertEqual(producto.stock_actual, 8)
    
    def test_03_detectar_stock_bajo(self):
        """Prueba: Detectar productos con stock bajo"""
        producto_normal = Producto.objects.create(
            codigo='TEST-003',
            nombre='Microondas',
            stock_actual=10,
            stock_minimo=3,
            precio_venta=180.00
        )
        
        producto_critico = Producto.objects.create(
            codigo='TEST-004',
            nombre='Ventilador',
            stock_actual=2,
            stock_minimo=5,
            precio_venta=45.00
        )
        
        self.assertTrue(producto_critico.stock_actual <= producto_critico.stock_minimo)
        self.assertFalse(producto_normal.stock_actual <= producto_normal.stock_minimo)
    
    def test_04_calcular_valor_inventario(self):
        """Prueba: Calcular el valor total del inventario"""
        Producto.objects.create(
            codigo='TEST-005',
            nombre='Producto 1',
            stock_actual=5,
            precio_venta=100.00
        )
        
        Producto.objects.create(
            codigo='TEST-006',
            nombre='Producto 2',
            stock_actual=3,
            precio_venta=200.00
        )
        
        productos = Producto.objects.all()
        valor_total = sum(p.stock_actual * p.precio_venta for p in productos)
        
        self.assertEqual(valor_total, 1100)
    
    def test_05_eliminar_producto(self):
        """Prueba: Eliminar un producto"""
        producto = Producto.objects.create(
            codigo='TEST-007',
            nombre='Producto a eliminar',
            precio_venta=50.00
        )
        
        producto_id = producto.id
        producto.delete()
        
        with self.assertRaises(Producto.DoesNotExist):
            Producto.objects.get(id=producto_id)
    
    # ========== PRUEBAS DE CATEGORÍAS ==========
    
    def test_06_crear_categoria(self):
        """Prueba: Crear una categoría"""
        self.assertEqual(self.categoria.nombre, 'Electrodomésticos')
        self.assertEqual(str(self.categoria), 'Electrodomésticos')
    
    def test_07_producto_con_categoria(self):
        """Prueba: Relacionar producto con categoría"""
        producto = Producto.objects.create(
            codigo='TEST-008',
            nombre='TV Samsung',
            categoria=self.categoria,
            precio_venta=650.00
        )
        
        self.assertEqual(producto.categoria.nombre, 'Electrodomésticos')
    
    # ========== PRUEBAS DE BODEGAS ==========
    
    def test_08_crear_bodega(self):
        """Prueba: Crear una bodega"""
        self.assertEqual(self.bodega.nombre, 'Bodega Principal')
        self.assertEqual(str(self.bodega), 'Bodega Principal')
    
    def test_09_producto_en_bodega(self):
        """Prueba: Asignar producto a una bodega"""
        producto = Producto.objects.create(
            codigo='TEST-009',
            nombre='Lavadora',
            bodega=self.bodega,
            precio_venta=800.00
        )
        
        self.assertEqual(producto.bodega.nombre, 'Bodega Principal')
    
    # ========== PRUEBAS DE PROVEEDORES ==========
    
    def test_10_crear_proveedor(self):
        """Prueba: Crear un proveedor"""
        self.assertEqual(self.proveedor.nombre, 'LG Electronics')
        self.assertEqual(self.proveedor.nit, '900123456-1')
    
    # ========== PRUEBAS DE LOTES ==========
    
    def test_11_crear_lote(self):
        """Prueba: Crear un lote de productos"""
        lote = Lote.objects.create(
            codigo='LOTE-001',
            proveedor=self.proveedor,
            fecha_pedido=date.today(),
            created_by=self.usuario
        )
        
        self.assertEqual(lote.codigo, 'LOTE-001')
        self.assertEqual(lote.estado, 'pendiente')
    
    def test_12_producto_con_serial(self):
        """Prueba: Crear producto con serial único"""
        lote = Lote.objects.create(
            codigo='LOTE-002',
            proveedor=self.proveedor,
            fecha_pedido=date.today(),
            created_by=self.usuario
        )
        
        producto_base = Producto.objects.create(
            codigo='TEST-010',
            nombre='Laptop HP',
            precio_venta=1500.00
        )
        
        producto_serial = ProductoConSerial.objects.create(
            lote=lote,
            producto_base=producto_base,
            serial='SN-123456789'
        )
        
        self.assertEqual(producto_serial.serial, 'SN-123456789')
        self.assertEqual(producto_serial.estado, 'disponible')
    
    # ========== PRUEBAS DE USUARIOS ==========
    
    def test_13_crear_usuario(self):
        """Prueba: Crear un usuario"""
        self.assertEqual(self.usuario.username, 'testuser')
        self.assertEqual(self.usuario.rol, 'admin')
    
    def test_14_usuario_puede_editar(self):
        """Prueba: Verificar propiedad puede_editar"""
        admin = Usuario.objects.create_user(username='admin2', password='123', rol='admin')
        almacenista = Usuario.objects.create_user(username='almacenista', password='123', rol='almacenista')
        consultor = Usuario.objects.create_user(username='consultor', password='123', rol='consultor')
        
        self.assertTrue(admin.puede_editar_productos)
        self.assertTrue(almacenista.puede_editar_productos)
        self.assertFalse(consultor.puede_editar_productos)
    
    def test_15_usuario_puede_ver_usuarios(self):
        """Prueba: Solo admin puede ver usuarios"""
        admin = Usuario.objects.create_user(username='admin3', password='123', rol='admin')
        almacenista = Usuario.objects.create_user(username='almacenista2', password='123', rol='almacenista')
        
        self.assertTrue(admin.puede_ver_usuarios)
        self.assertFalse(almacenista.puede_ver_usuarios)