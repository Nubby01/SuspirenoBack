"""Filtros de plantilla para montos y cantidades."""

from django import template

register = template.Library()


@register.filter
def pesos(valor):
    """Muestra un monto en pesos chilenos."""
    if valor is None:
        return "—"
    return "$" + f"{int(round(float(valor))):,}".replace(",", ".")


@register.filter
def cantidad(valor):
    """Cantidad sin ceros de más."""
    if valor is None:
        return "0"
    numero = float(valor)
    if numero.is_integer():
        return str(int(numero))
    return f"{numero:g}"
