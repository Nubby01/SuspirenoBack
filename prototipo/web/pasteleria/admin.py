"""Registro de modelos en el admin de Django (soporte)."""

from django.contrib import admin

from .models import (
    Cliente,
    CompraInsumo,
    Cotizacion,
    CotizacionProducto,
    Insumo,
    Pedido,
    PedidoProducto,
    Producto,
    ProductoInsumo,
    Usuario,
)


admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Insumo)
admin.site.register(Producto)
admin.site.register(ProductoInsumo)
admin.site.register(Cotizacion)
admin.site.register(CotizacionProducto)
admin.site.register(Pedido)
admin.site.register(PedidoProducto)
admin.site.register(CompraInsumo)
