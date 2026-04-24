from django.db import models
from django.contrib.auth.models import User


# 🧁 PRODUCTOS 
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.FloatField()
    descripcion = models.TextField(null=True, blank=True)
    imagen = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.nombre


# 🎂 PEDIDOS
class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio = models.FloatField()
    mensaje = models.TextField()
    personas = models.IntegerField()
    fecha = models.DateField()
    estado = models.CharField(max_length=50, default='Pendiente')

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"