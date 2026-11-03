"""Variables disponibles en todas las plantillas."""

from .menu import GRUPOS_NAV


def carrito(request):
    """Carrito de sesión y filtros del catálogo."""
    datos = request.session.get("carrito", {})
    return {
        "carrito_cantidad": sum(int(cantidad) for cantidad in datos.values()),
        "grupos_nav": GRUPOS_NAV,
        "q": request.GET.get("q", ""),
        "categoria": request.GET.get("categoria", ""),
        "grupo": request.GET.get("grupo", ""),
        "ultima_cotizacion": request.session.get("ultima_cotizacion"),
    }
