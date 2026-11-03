"""Reglas de negocio: cotización, stock y estados del pedido."""
from datetime import date, timedelta

from django.db import transaction

from .models import CompraInsumo, Cotizacion, Pedido, PedidoProducto


class ReglaNegocioError(Exception):
    pass


def consumo_insumos(lineas):
    """Suma insumos según receta y cantidad pedida."""
    acumulado = {}
    for producto, cantidad in lineas:
        for ingrediente in producto.receta.all():
            actual = acumulado.get(ingrediente.insumo_id)
            if actual is None:
                acumulado[ingrediente.insumo_id] = [ingrediente.insumo, ingrediente.cantidad * cantidad]
            else:
                actual[1] += ingrediente.cantidad * cantidad
    return [(insumo, cantidad) for insumo, cantidad in acumulado.values()]


def faltantes_de(lineas):
    return sorted(insumo.nombre for insumo, cantidad in consumo_insumos(lineas) if insumo.stock_actual < cantidad)


@transaction.atomic
def convertir_cotizacion(cotizacion, usuario, fecha_entrega, abono, canal_despacho):
    if cotizacion.estado != Cotizacion.ENVIADA:
        raise ReglaNegocioError("Esta cotización ya fue convertida en pedido.")
    hoy = date.today()
    if fecha_entrega < hoy:
        raise ReglaNegocioError("La fecha de entrega no puede ser anterior a hoy.")
    if fecha_entrega > hoy + timedelta(days=365):
        raise ReglaNegocioError("La entrega no puede ser a más de un año desde hoy.")
    if abono > cotizacion.total:
        raise ReglaNegocioError("El abono no puede superar el total de la cotización.")
    if canal_despacho == "Despacho" and not cotizacion.cliente.direccion:
        raise ReglaNegocioError("El cliente no indicó dirección para el despacho.")

    cotizacion.estado = Cotizacion.CONVERTIDA
    cotizacion.save(update_fields=["estado"])
    pedido = Pedido.objects.create(
        cotizacion=cotizacion,
        registrado_por=usuario,
        fecha_pedido=date.today(),
        fecha_entrega=fecha_entrega,
        monto_total=cotizacion.total,
        abono=abono,
        estado=Pedido.PENDIENTE,
        canal_despacho=canal_despacho,
        stock_descontado=False,
    )
    for linea in cotizacion.lineas.select_related("producto"):
        PedidoProducto.objects.create(
            pedido=pedido,
            producto=linea.producto,
            formato=linea.formato,
            cantidad=linea.cantidad,
            precio=linea.precio,
            subtotal=linea.subtotal,
        )
    return pedido


@transaction.atomic
def descontar_stock(pedido):
    if pedido.stock_descontado:
        return
    lineas = [(linea.producto, linea.cantidad) for linea in pedido.lineas.select_related("producto")]
    faltantes = faltantes_de(lineas)
    if faltantes:
        raise ReglaNegocioError("Stock insuficiente de: " + ", ".join(faltantes) + ".")
    for insumo, cantidad in consumo_insumos(lineas):
        insumo.stock_actual -= cantidad
        insumo.save(update_fields=["stock_actual"])
    pedido.stock_descontado = True
    pedido.save(update_fields=["stock_descontado"])


@transaction.atomic
def cambiar_estado(pedido, nuevo_estado):
    if nuevo_estado not in Pedido.TRANSICIONES[pedido.estado]:
        raise ReglaNegocioError(f"No se puede pasar de {pedido.estado} a {nuevo_estado}.")
    if nuevo_estado == Pedido.CONFIRMADO:
        descontar_stock(pedido)
    pedido.estado = nuevo_estado
    pedido.save(update_fields=["estado"])


@transaction.atomic
def registrar_compra(insumo, datos):
    compra = CompraInsumo.objects.create(insumo=insumo, **datos)
    insumo.stock_actual += compra.cantidad_comprada
    insumo.save(update_fields=["stock_actual"])
    return compra
