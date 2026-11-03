"""Reportes del panel: ventas, ticket y stock bajo."""

from datetime import date, timedelta

from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView

from ..mixins import PanelMixin
from ..models import CompraInsumo, Insumo, Pedido, PedidoProducto


class ReportesView(PanelMixin, TemplateView):
    template_name = "panel/reportes.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        vigentes = Pedido.objects.vigentes()
        confirmados = vigentes.exclude(estado=Pedido.PENDIENTE)
        resumen = confirmados.aggregate(
            vendido=Coalesce(Sum("monto_total"), 0),
            abonado=Coalesce(Sum("abono"), 0),
            ticket=Avg("monto_total"),
        )
        resumen["pedidos"] = vigentes.count()
        conteo = {
            fila["estado"]: fila
            for fila in Pedido.objects.values("estado").annotate(cantidad=Count("id"), monto=Coalesce(Sum("monto_total"), 0))
        }
        por_estado = []
        for estado, _etiqueta in Pedido.ESTADOS:
            fila = conteo.get(estado, {})
            por_estado.append({
                "estado": estado,
                "clase": estado.lower().replace(" ", "-"),
                "cantidad": fila.get("cantidad", 0),
                "monto": fila.get("monto", 0),
            })
        ranking = list(
            PedidoProducto.objects.filter(pedido__in=confirmados)
            .values("producto__nombre", "producto__categoria")
            .annotate(unidades=Sum("cantidad"), monto=Sum("subtotal"))
            .order_by("-unidades")[:6]
        )
        por_categoria = list(
            PedidoProducto.objects.filter(pedido__in=confirmados)
            .values("producto__categoria")
            .annotate(unidades=Sum("cantidad"), monto=Sum("subtotal"))
            .order_by("-monto")
        )
        hoy = date.today()
        contexto.update({
            "resumen": resumen,
            "saldo": resumen["vendido"] - resumen["abonado"],
            "por_estado": por_estado,
            "ranking": ranking,
            "por_categoria": por_categoria,
            "grafico": {
                "etiquetas": [fila["producto__nombre"] for fila in ranking],
                "unidades": [fila["unidades"] or 0 for fila in ranking],
            },
            "insumos_bajos": Insumo.objects.filter(stock_actual__lte=F("stock_minimo")),
            "por_vencer": CompraInsumo.objects.filter(
                fecha_vencimiento__range=(hoy, hoy + timedelta(days=3))
            ).select_related("insumo"),
            "recientes": Pedido.objects.con_detalle()[:8],
        })
        return contexto
