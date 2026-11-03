from django.shortcuts import redirect


class ClaveProvisoriaMiddleware:
    """Si la clave es provisoria, manda a cambiarla antes de seguir."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        usuario = getattr(request, "user", None)
        if (
            usuario is not None
            and usuario.is_authenticated
            and getattr(usuario, "debe_cambiar_clave", False)
        ):
            ruta = request.path
            permitidas = ("/panel/cuenta/", "/cuentas/salir/", "/static/", "/media/")
            if not ruta.startswith(permitidas):
                return redirect("panel_cuenta")
        return self.get_response(request)
