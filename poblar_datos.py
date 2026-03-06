# poblar_datos.py
import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Perfil
from ofertas.models import Categoria, Oferta, Comentario, Calificacion, Favorito

print("🚀 COMENZANDO A POBLAR LA BASE DE DATOS...")
print("=" * 50)

# ==================== PASO 1: CREAR USUARIOS ====================
print("\n📌 PASO 1: Creando usuarios (30 usuarios)...")

# Crear consumidores (25 consumidores)
for i in range(1, 26):
    user, created = User.objects.get_or_create(
        username=f'consumidor{i}',
        defaults={
            'email': f'consumidor{i}@email.com',
            'first_name': f'Nombre{i}',
            'last_name': f'Apellido{i}',
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        user.perfil.rol = 'consumidor'
        user.perfil.nombre_completo = f'Consumidor {i}'
        user.perfil.telefono = f'300{random.randint(1000000, 9999999)}'
        user.perfil.direccion = f'Calle {random.randint(1, 100)} #{random.randint(1, 50)}-{random.randint(1, 50)}'
        user.perfil.descripcion = f'Soy un consumidor frecuente de EndlessOffers'
        user.perfil.save()
        print(f"  ✅ Consumidor {i} creado")
    else:
        print(f"  ⏩ Consumidor {i} ya existe")

# Crear proveedores (10 proveedores)
proveedores_lista = [
    {'username': 'alkosto', 'email': 'alkosto@gmail.com', 'nombre': 'Alkosto', 'web': 'https://www.alkosto.com'},
    {'username': 'exito', 'email': 'exito@gmail.com', 'nombre': 'Éxito', 'web': 'https://www.exito.com'},
    {'username': 'falabella', 'email': 'falabella@gmail.com', 'nombre': 'Falabella', 'web': 'https://www.falabella.com.co'},
    {'username': 'jumbo', 'email': 'jumbo@gmail.com', 'nombre': 'Jumbo', 'web': 'https://www.tiendasjumbo.co'},
    {'username': 'mercadolibre', 'email': 'ml@gmail.com', 'nombre': 'Mercado Libre', 'web': 'https://www.mercadolibre.com.co'},
    {'username': 'k_tronix', 'email': 'ktronix@gmail.com', 'nombre': 'Ktronix', 'web': 'https://www.ktronix.com'},
    {'username': 'panamericana', 'email': 'panamericana@gmail.com', 'nombre': 'Panamericana', 'web': 'https://www.panamericana.com.co'},
    {'username': 'homecenter', 'email': 'homecenter@gmail.com', 'nombre': 'Homecenter', 'web': 'https://www.homecenter.com.co'},
    {'username': 'olimpica', 'email': 'olimpica@gmail.com', 'nombre': 'Olimpica', 'web': 'https://www.olimpica.com'},
    {'username': 'd1', 'email': 'd1@gmail.com', 'nombre': 'D1', 'web': 'https://www.d1.com.co'},
]

for p in proveedores_lista:
    user, created = User.objects.get_or_create(
        username=p['username'],
        defaults={
            'email': p['email'],
            'first_name': p['nombre'],
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        user.perfil.rol = 'proveedor'
        user.perfil.nombre_completo = p['nombre']
        user.perfil.telefono = f'310{random.randint(1000000, 9999999)}'
        user.perfil.direccion = f'Carrera {random.randint(1, 100)} #{random.randint(1, 50)}-{random.randint(1, 50)}'
        user.perfil.descripcion = f'{p["nombre"]} es una empresa líder en ventas con los mejores precios del mercado.'
        user.perfil.sitio_web = p['web']
        user.perfil.verificado = random.choice([True, False])  # Algunos verificados, otros no
        user.perfil.save()
        print(f"  ✅ Proveedor {p['nombre']} creado")
    else:
        print(f"  ⏩ Proveedor {p['nombre']} ya existe")

# ==================== PASO 2: CREAR CATEGORÍAS ====================
print("\n📌 PASO 2: Creando categorías (16 categorías)...")

categorias_lista = [
    'Electrodomésticos', 'Tecnología', 'Hogar', 'Moda', 
    'Deportes', 'Belleza', 'Juguetes', 'Mascotas',
    'Libros', 'Videojuegos', 'Muebles', 'Herramientas',
    'Jardinería', 'Automotriz', 'Salud', 'Bebés'
]

categorias = []
for cat_nombre in categorias_lista:
    cat, created = Categoria.objects.get_or_create(nombre=cat_nombre)
    categorias.append(cat)
    if created:
        print(f"  ✅ Categoría '{cat_nombre}' creada")
    else:
        print(f"  ⏩ Categoría '{cat_nombre}' ya existe")

# ==================== PASO 3: CREAR 20 OFERTAS ====================
print("\n📌 PASO 3: Creando 20 ofertas...")

proveedores = User.objects.filter(perfil__rol='proveedor')
if not proveedores:
    print("  ❌ No hay proveedores. Primero crea proveedores.")
else:
    productos = [
        # Tecnología (5 ofertas)
        {
            'titulo': 'TV TCL 50" Pulgadas 127 cm 50S5K FHD QLED',
            'descripcion': 'TV TCL serie S5K: Este TV combina la tecnología de imagen QLED con FHD. Su avanzada pantalla QLED optimiza en tiempo real la precisión de colores y brillos. Disfruta de Dolby Audio para obtener la mejor calidad de sonido.',
            'precio_original': 2999000,
            'precio_descuento': 1149000,
            'categoria': 'Tecnología'
        },
        {
            'titulo': 'Celular HONOR Magic 8 Lite 512GB 5G',
            'descripcion': 'Smartphone de alta gama con pantalla AMOLED de 6.7 pulgadas, 8GB RAM, 512GB almacenamiento y cámara triple de 108MP. Batería de 5000mAh con carga rápida.',
            'precio_original': 2299000,
            'precio_descuento': 1799000,
            'categoria': 'Tecnología'
        },
        {
            'titulo': 'Portátil HP Pavilion 15.6"',
            'descripcion': 'Portátil HP Pavilion con procesador Intel Core i5 de 12va generación, 16GB RAM, 512GB SSD, pantalla Full HD. Ideal para trabajo y estudio.',
            'precio_original': 3499000,
            'precio_descuento': 2999000,
            'categoria': 'Tecnología'
        },
        {
            'titulo': 'Tablet Samsung Galaxy Tab S9',
            'descripcion': 'Tablet Samsung Galaxy Tab S9 con pantalla de 11 pulgadas, procesador Snapdragon 8 Gen 2, 8GB RAM, 128GB almacenamiento. Incluye S Pen.',
            'precio_original': 2799000,
            'precio_descuento': 2399000,
            'categoria': 'Tecnología'
        },
        {
            'titulo': 'Audífonos Sony WH-1000XM4',
            'descripcion': 'Audífonos inalámbricos con cancelación de ruido líder en la industria, 30 horas de batería, carga rápida y sonido de alta calidad.',
            'precio_original': 899000,
            'precio_descuento': 699000,
            'categoria': 'Tecnología'
        },
        
        # Electrodomésticos (4 ofertas)
        {
            'titulo': 'Lavadora LG 19kg Inverter',
            'descripcion': 'Lavadora de carga frontal con tecnología Inverter, 19kg de capacidad, 6 Motion, Wi-Fi integrado, inteligencia artificial para optimizar lavados.',
            'precio_original': 1999000,
            'precio_descuento': 1599000,
            'categoria': 'Electrodomésticos'
        },
        {
            'titulo': 'Nevera Samsung 350L',
            'descripcion': 'Nevera de dos puertas con capacidad de 350L, tecnología No Frost, dispensador de agua, iluminación LED y control digital de temperatura.',
            'precio_original': 2499000,
            'precio_descuento': 2199000,
            'categoria': 'Electrodomésticos'
        },
        {
            'titulo': 'Horno Microondas Haceb 25L',
            'descripcion': 'Horno microondas de 25 litros con 8 programas automáticos, descongelación rápida, panel digital y acabado en acero inoxidable.',
            'precio_original': 399000,
            'precio_descuento': 329000,
            'categoria': 'Electrodomésticos'
        },
        {
            'titulo': 'Aspiradora Robot Xiaomi',
            'descripcion': 'Aspiradora robot inteligente con mapeo láser, 3000Pa de succión, control por app, compatible con Alexa, autonomía de 150 minutos.',
            'precio_original': 899000,
            'precio_descuento': 749000,
            'categoria': 'Electrodomésticos'
        },
        
        # Hogar (3 ofertas)
        {
            'titulo': 'Juego de Ollas 10 piezas',
            'descripcion': 'Juego de ollas de acero inoxidable con fondo difusor, 10 piezas incluye ollas de diferentes tamaños, sartén y tapas de vidrio.',
            'precio_original': 299000,
            'precio_descuento': 229000,
            'categoria': 'Hogar'
        },
        {
            'titulo': 'Edredón King Size',
            'descripcion': 'Edredón tamaño king size de microfibra, suave y cálido, disponible en varios colores, incluye dos fundas.',
            'precio_original': 199000,
            'precio_descuento': 149000,
            'categoria': 'Hogar'
        },
        {
            'titulo': 'Set de Toallas 6 piezas',
            'descripcion': 'Set de 6 toallas de baño de algodón egipcio de alta calidad, suaves y absorbentes, disponibles en varios colores.',
            'precio_original': 129000,
            'precio_descuento': 99000,
            'categoria': 'Hogar'
        },
        
        # Moda (3 ofertas)
        {
            'titulo': 'Zapatos Nike Air Max',
            'descripcion': 'Zapatillas deportivas con amortiguación Air Max, ideales para correr y uso diario, disponibles en varias tallas y colores.',
            'precio_original': 399000,
            'precio_descuento': 299000,
            'categoria': 'Moda'
        },
        {
            'titulo': 'Camisa Polo Lacoste',
            'descripcion': 'Camisa tipo polo de la marca Lacoste, 100% algodón, logo bordado, disponibles en varios colores.',
            'precio_original': 189000,
            'precio_descuento': 149000,
            'categoria': 'Moda'
        },
        {
            'titulo': 'Jeans Levis 501',
            'descripcion': 'Jeans clásicos Levis 501, corte original, 100% algodón, disponibles en varias tallas y colores.',
            'precio_original': 229000,
            'precio_descuento': 189000,
            'categoria': 'Moda'
        },
        
        # Deportes (3 ofertas)
        {
            'titulo': 'Bicicleta GW Victory',
            'descripcion': 'Bicicleta GW Victory, rodada 29, cambios Shimano 21 velocidades, frenos de disco mecánicos, cuadro de aluminio.',
            'precio_original': 1299000,
            'precio_descuento': 1099000,
            'categoria': 'Deportes'
        },
        {
            'titulo': 'Pesa Rusa 16kg',
            'descripcion': 'Pesa rusa de hierro fundido con base plana, peso 16kg, ideal para entrenamiento funcional y crossfit.',
            'precio_original': 129000,
            'precio_descuento': 99000,
            'categoria': 'Deportes'
        },
        {
            'titulo': 'Balón de Fútbol Golty',
            'descripcion': 'Balón de fútbol Golty Profesional, cosido a máquina, vejiga de látex, tamaño 5, ideal para canchas sintéticas.',
            'precio_original': 99000,
            'precio_descuento': 79000,
            'categoria': 'Deportes'
        },
        
        # Belleza (2 ofertas)
        {
            'titulo': 'Perfume Carolina Herrera Bad Boy',
            'descripcion': 'Perfume para hombre de la colección Bad Boy, aroma amaderado y especiado, presentación de 100ml.',
            'precio_original': 299000,
            'precio_descuento': 249000,
            'categoria': 'Belleza'
        },
        {
            'titulo': 'Set de Maquillaje Profesional',
            'descripcion': 'Set de maquillaje profesional con 120 sombras, labiales, brochas y accesorios, estuche de regalo.',
            'precio_original': 159000,
            'precio_descuento': 129000,
            'categoria': 'Belleza'
        },
    ]

    for producto in productos:
        proveedor = random.choice(proveedores)
        categoria_nombre = producto['categoria']
        categoria = Categoria.objects.get(nombre=categoria_nombre)
        
        # Crear fecha aleatoria (últimos 30 días)
        dias_atras = random.randint(0, 30)
        fecha_creacion = timezone.now() - timedelta(days=dias_atras)
        
        oferta, created = Oferta.objects.get_or_create(
            titulo=producto['titulo'],
            proveedor=proveedor.perfil,
            defaults={
                'descripcion': producto['descripcion'],
                'precio_original': producto['precio_original'],
                'precio_descuento': producto['precio_descuento'],
                'estado': random.choice(['activa', 'activa', 'activa', 'pendiente']),
                'fecha_creacion': fecha_creacion,
            }
        )
        if created:
            oferta.categorias.add(categoria)
            # Calcular porcentaje de descuento
            oferta.porcentaje_descuento = ((producto['precio_original'] - producto['precio_descuento']) / producto['precio_original']) * 100
            oferta.save()
            print(f"  ✅ Oferta '{producto['titulo']}' creada (proveedor: {proveedor.username})")
        else:
            print(f"  ⏩ Oferta '{producto['titulo']}' ya existe")

# ==================== PASO 4: CREAR COMENTARIOS Y CALIFICACIONES ====================
print("\n📌 PASO 4: Creando comentarios y calificaciones...")

ofertas = Oferta.objects.filter(estado='activa')
usuarios = User.objects.filter(perfil__rol='consumidor')

if ofertas and usuarios:
    comentarios_ejemplo = [
        "Excelente producto, llegó rápido y en perfectas condiciones.",
        "Muy buena calidad, superó mis expectativas.",
        "El envío fue rápido, pero el empaque llegó un poco golpeado.",
        "Producto tal como lo describen, muy satisfecho.",
        "La relación precio-calidad es increíble, lo recomiendo.",
        "Buen producto, pero el servicio al cliente podría mejorar.",
        "Me encantó, volvería a comprar sin dudarlo.",
        "Funciona perfectamente, tal como esperaba.",
        "El vendedor fue muy atento y resolvió todas mis dudas.",
        "Producto de excelente calidad, 100% recomendado.",
        "Llegó antes de lo esperado, muy buen servicio.",
        "El empaque venía perfecto, todo muy bien protegido.",
        "El producto es original y de buena calidad.",
        "Lo compré para regalar y le encantó a la persona.",
        "Buena atención al cliente, resolvieron mis dudas rápidamente.",
        "El producto tiene pequeños detalles, pero por el precio está bien.",
        "Excelente compra, volvería a comprar en esta tienda.",
        "La relación calidad-precio es muy buena.",
        "El producto funciona correctamente, tal como lo esperaba.",
        "Muy contento con mi compra, lo recomiendo ampliamente.",
    ]

    comentarios_creados = 0
    calificaciones_creadas = 0
    
    for oferta in ofertas:
        # Comentarios (entre 2 y 8 por oferta)
        num_comentarios = random.randint(2, 8)
        for _ in range(num_comentarios):
            usuario = random.choice(usuarios)
            comentario = random.choice(comentarios_ejemplo)
            
            # Fecha aleatoria (últimos 20 días)
            dias_atras = random.randint(0, 20)
            fecha = timezone.now() - timedelta(days=dias_atras)
            
            _, created = Comentario.objects.get_or_create(
                usuario=usuario,
                oferta=oferta,
                defaults={
                    'contenido': comentario,
                    'fecha_creacion': fecha
                }
            )
            if created:
                comentarios_creados += 1
        
        # Calificaciones (entre 5 y 15 por oferta)
        num_calificaciones = random.randint(5, 15)
        for _ in range(num_calificaciones):
            usuario = random.choice(usuarios)
            puntuacion = random.randint(3, 5)  # Mayoría calificaciones positivas
            
            _, created = Calificacion.objects.get_or_create(
                usuario=usuario,
                oferta=oferta,
                defaults={'puntuacion': puntuacion}
            )
            if created:
                calificaciones_creadas += 1
    
    print(f"  ✅ {comentarios_creados} comentarios creados")
    print(f"  ✅ {calificaciones_creadas} calificaciones creadas")

# ==================== PASO 5: CREAR FAVORITOS ====================
print("\n📌 PASO 5: Creando favoritos...")

ofertas_lista = list(Oferta.objects.filter(estado='activa'))
usuarios = User.objects.all()
favoritos_creados = 0

if ofertas_lista and usuarios:
    for usuario in usuarios:
        # Cada usuario tiene entre 3 y 10 favoritos
        num_favoritos = random.randint(3, 10)
        num_favoritos = min(num_favoritos, len(ofertas_lista))
        ofertas_seleccionadas = random.sample(ofertas_lista, num_favoritos)
        
        for oferta in ofertas_seleccionadas:
            _, created = Favorito.objects.get_or_create(
                usuario=usuario,
                oferta=oferta
            )
            if created:
                favoritos_creados += 1
    
    print(f"  ✅ {favoritos_creados} favoritos creados")

# ==================== ESTADÍSTICAS FINALES ====================
print("\n" + "=" * 50)
print("📊 ESTADÍSTICAS FINALES")
print("=" * 50)

print(f"👥 Usuarios totales: {User.objects.count()}")
print(f"  ├─ Consumidores: {User.objects.filter(perfil__rol='consumidor').count()}")
print(f"  └─ Proveedores: {User.objects.filter(perfil__rol='proveedor').count()}")

print(f"\n🏷️ Categorías: {Categoria.objects.count()}")

print(f"\n🛍️ Ofertas totales: {Oferta.objects.count()}")
print(f"  ├─ Activas: {Oferta.objects.filter(estado='activa').count()}")
print(f"  ├─ Pendientes: {Oferta.objects.filter(estado='pendiente').count()}")
print(f"  └─ Rechazadas: {Oferta.objects.filter(estado='rechazada').count()}")

print(f"\n💬 Comentarios: {Comentario.objects.count()}")
print(f"⭐ Calificaciones: {Calificacion.objects.count()}")
print(f"❤️ Favoritos: {Favorito.objects.count()}")

print("\n" + "=" * 50)
print("🎉 ¡BASE DE DATOS POBLADA EXITOSAMENTE!")
print("=" * 50)