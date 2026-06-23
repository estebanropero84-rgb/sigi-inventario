import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sigi_admin.settings')
django.setup()

from django.db import connection

def crear_tabla_ubicacion():
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "Productos_ubicacion" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "nombre" varchar(100) NOT NULL UNIQUE,
                "descripcion" text NULL,
                "creado_en" timestamp with time zone NOT NULL
            );
        """)
        print("✅ Tabla Productos_ubicacion creada correctamente")

if __name__ == "__main__":
    crear_tabla_ubicacion()