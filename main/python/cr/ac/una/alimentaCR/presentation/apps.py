from django.apps import AppConfig


class PresentationConfig(AppConfig):
    """
    Configuracion de la capa de presentacion.
    """

    name = "cr.ac.una.alimentaCR.presentation"

    def ready(self):
        from . import openapi  # noqa: F401