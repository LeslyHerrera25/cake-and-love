from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('personalizar/<int:producto_id>/', views.personalizar, name='personalizar'),
    path('eliminar/<int:index>/', views.eliminar_del_carrito, name='eliminar'),
    path('confirmar/', views.confirmar_pedido, name='confirmar'),
    path('pedidos/', views.ver_pedidos, name='pedidos'),
    path('reportes/', views.reportes, name='reportes'),
    path('actualizar_estado/<int:pedido_id>/', views.actualizar_estado, name='actualizar_estado'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('redirigir/', views.redireccionar_por_rol, name='redireccionar_por_rol'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('pago/', views.pago, name='pago'),
]