from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


class PanelMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo equipo interno (admin y ayudante)."""

    def test_func(self):
        return self.request.user.entra_al_panel


class SoloAdministradoraMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Acciones exclusivas de la administradora."""

    def test_func(self):
        return self.request.user.es_administradora


class FormularioMixin:
    """Agrega título y enlace de vuelta al contexto del formulario."""

    titulo = ""
    volver_url = "reportes"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = self.titulo
        contexto["volver"] = reverse(self.volver_url)
        return contexto


class EliminarModalMixin:
    """El borrado se confirma en el modal; GET solo redirige."""

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            destino = self.get_success_url()
        except Exception:
            destino = reverse(getattr(self, "volver_url", "reportes"))
        return redirect(destino)