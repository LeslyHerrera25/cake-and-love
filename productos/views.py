from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Producto, Pedido
from django.contrib.auth import logout

from datetime import date, datetime, timedelta

from django.contrib import messages

# 🔐 VALIDACIONES DE GRUPO
def es_admin(user):
    return user.is_authenticated and user.groups.filter(name__iexact='administrador').exists()

def es_empleado(user):
    return user.is_authenticated and user.groups.filter(name__iexact='empleado').exists()

def es_cliente(user):
    return user.is_authenticated and user.groups.filter(name__iexact='cliente').exists()


# 🏠 INICIO
def inicio(request):
    return render(request, 'productos/inicio.html')


# 🛍️ CATÁLOGO
@login_required
def catalogo(request):
    if not es_cliente(request.user):
        return HttpResponse("No autorizado")

    productos = Producto.objects.all()
    return render(request, 'productos/catalogo.html', {'productos': productos})


# 🛒 CARRITO
@login_required
def ver_carrito(request):
    if not es_cliente(request.user):
        return HttpResponse("No autorizado")

    carrito = request.session.get('carrito', [])
    productos = [item for item in carrito if isinstance(item, dict)]
    total = sum(item['precio'] for item in productos)

    return render(request, 'productos/carrito.html', {
        'productos': productos,
        'total': total
    })


# 🎂 PERSONALIZAR
@login_required
def personalizar(request, producto_id):
    if not es_cliente(request.user):
        return HttpResponse("No autorizado")

    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':

        # 🔥 VALIDACIÓN DE FECHA
        fecha_str = request.POST.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

        fecha_minima = datetime.now().date() + timedelta(days=4)

        if fecha < fecha_minima:
            messages.error(request, "Debes elegir una fecha mínima de 4 días.")
            return redirect('personalizar', producto_id=producto.id)

        # 🛒 CARRITO
        carrito = request.session.get('carrito', [])

        item = {
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'mensaje': request.POST.get('mensaje'),
            'personas': request.POST.get('personas'),
            'fecha': fecha_str,
        }

        carrito.append(item)

        request.session['carrito'] = carrito
        request.session.modified = True

        return redirect('carrito')

    return render(request, 'productos/personalizar.html', {
        'producto': producto
    })


# ❌ ELIMINAR DEL CARRITO
@login_required
def eliminar_del_carrito(request, index):
    if not es_cliente(request.user):
        return HttpResponse("No autorizado")

    carrito = request.session.get('carrito', [])

    if index < len(carrito):
        carrito.pop(index)

    request.session['carrito'] = carrito
    request.session.modified = True

    return redirect('carrito')


# 🧁 CONFIRMAR PEDIDO
@login_required
def confirmar_pedido(request):
    if not es_cliente(request.user):
        return HttpResponse("No tienes permiso para comprar")

    carrito = request.session.get('carrito', [])

    if not carrito:
        return HttpResponse("El carrito está vacío")

    for item in carrito:
        if isinstance(item, dict):
            Pedido.objects.create(
                usuario=request.user,
                nombre=item['nombre'],
                precio=item['precio'],
                mensaje=item['mensaje'],
                personas=item['personas'],
                fecha=item['fecha']
            )

    
    request.session['carrito'] = []
    request.session.modified = True

    
    return redirect('mis_pedidos')


# 🧁 EMPLEADO VE PEDIDOS
@login_required
def ver_pedidos(request):
    if not es_empleado(request.user):
        return HttpResponse("No autorizado")

    pedidos = Pedido.objects.all()

    return render(request, 'productos/lista_pedidos.html', {
        'pedidos': pedidos
    })


# 🧁 ACTUALIZAR ESTADO
@login_required
def actualizar_estado(request, pedido_id):
    if not es_empleado(request.user):
        return HttpResponse("No autorizado")

    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        pedido.estado = nuevo_estado
        pedido.save()

    return redirect('pedidos')


# 🧁 CLIENTE VE SUS PEDIDOS
@login_required
def mis_pedidos(request):
    if not es_cliente(request.user):
        return HttpResponse("No autorizado")

    pedidos = Pedido.objects.filter(usuario=request.user)

    return render(request, 'productos/mis_pedidos.html', {
        'pedidos': pedidos
    })



# 🧁 ADMIN VE REPORTES
@login_required
def reportes(request):
    if not es_admin(request.user):
        return HttpResponse("No autorizado")

    # Todos los pedidos
    pedidos = Pedido.objects.all()

    # Totales generales
    total_pedidos = pedidos.count()

    # Solo ventas reales (Entregado)
    ventas_entregadas = Pedido.objects.filter(estado='Entregado')

    total_ventas = sum(p.precio for p in ventas_entregadas)

    # Fechas para reportes
    hoy = date.today()
    hace_7_dias = hoy - timedelta(days=7)
    hace_30_dias = hoy - timedelta(days=30)

    # Ventas semanales
    ventas_semanales = Pedido.objects.filter(
        estado='Entregado',
        fecha__gte=hace_7_dias
    )

    total_semanal = sum(p.precio for p in ventas_semanales)

    # Ventas mensuales
    ventas_mensuales = Pedido.objects.filter(
        estado='Entregado',
        fecha__gte=hace_30_dias
    )

    total_mensual = sum(p.precio for p in ventas_mensuales)

    # Pedidos por estado
    pendientes = Pedido.objects.filter(estado='Pendiente').count()
    en_proceso = Pedido.objects.filter(estado='En proceso').count()
    listos = Pedido.objects.filter(estado='Listo').count()
    entregados = Pedido.objects.filter(estado='Entregado').count()

    return render(request, 'productos/reportes.html', {
        'total_pedidos': total_pedidos,
        'total_ventas': total_ventas,

        'total_semanal': total_semanal,
        'total_mensual': total_mensual,

        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'listos': listos,
        'entregados': entregados,
    })


# REDIRECCIÓN POR ROL
@login_required
def redireccionar_por_rol(request):

    if es_admin(request.user):
        return redirect('reportes')

    elif es_empleado(request.user):
        return redirect('pedidos')

    elif es_cliente(request.user):
        return redirect('catalogo')

    else:
        return redirect('login')


def cerrar_sesion(request):
    logout(request)
    return redirect('login')

@login_required
def pago(request):
    if not es_cliente(request.user):
        return HttpResponse("No autorizado")

    carrito = request.session.get('carrito', [])

    if not carrito:
        return redirect('carrito')

    total = sum(item['precio'] for item in carrito if isinstance(item, dict))

    if request.method == 'POST':
        # 💾 Guardar pedidos después del "pago"
        for item in carrito:
            if isinstance(item, dict):
                Pedido.objects.create(
                    usuario=request.user,
                    nombre=item['nombre'],
                    precio=item['precio'],
                    mensaje=item['mensaje'],
                    personas=item['personas'],
                    fecha=item['fecha']
                )

        request.session['carrito'] = []
        request.session.modified = True

        return redirect('mis_pedidos')

    return render(request, 'productos/pago.html', {
        'total': total
    })
   