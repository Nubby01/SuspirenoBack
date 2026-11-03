"""Arma el enlace de WhatsApp para confirmar una cotización."""

from urllib.parse import quote

from django.conf import settings


def pesos(valor):
    """Formato de pesos chilenos."""
    return "$" + f"{int(round(valor)):,}".replace(",", ".")


def enlace_whatsapp(cotizacion):
    """Mensaje listo para enviar por WhatsApp."""
    lineas = [f"Hola, quiero confirmar la cotización N° {cotizacion.pk}:"]
    lineas += [
        f"- {linea.cantidad} x {linea.producto.nombre}"
        f"{' (' + linea.formato + ')' if linea.formato else ''}: {pesos(linea.subtotal)}"
        for linea in cotizacion.lineas.all()
    ]
    lineas.append(f"Total: {pesos(cotizacion.total)}")
    texto = quote("\n".join(lineas))
    return f"https://wa.me/{settings.WHATSAPP_NUMERO}?text={texto}"
