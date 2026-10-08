"""
Pruebas del manejador global de errores (Problem Details, RFC 9457).
No necesitan base de datos: lanzan cada excepcion desde una vista de
prueba y verifican codigo, tipo de contenido y que no se filtre traza.
"""
import pytest
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business import exceptions as e


def responder_con(excepcion):
    class VistaDePrueba(APIView):
        authentication_classes = []
        permission_classes = []

        def get(self, request):
            raise excepcion

    respuesta = VistaDePrueba.as_view()(
        APIRequestFactory().get("/api/v1/x")
    )
    respuesta.render()
    return respuesta


@pytest.mark.parametrize(
    "excepcion, codigo",
    [
        (e.SolicitudNoExisteError("no existe"), 404),
        (e.OrganizacionNoExisteError("no existe"), 404),
        (e.CategoriaNoExisteError("no existe"), 404),
        (e.UsuarioNoExisteError("no existe"), 404),
        (e.DonacionNoExisteError("no existe"), 404),
        (e.EntregaNoExisteError("no existe"), 404),
        (e.SolicitudNoPendienteError("no pendiente"), 409),
        (e.DonacionNoDisponibleError("no disponible"), 409),
        (e.CorreoDuplicadoError("correo repetido"), 409),
        (e.SolicitudDuplicadaError("duplicada"), 409),
        (e.EntregaNoPendienteError("no pendiente"), 409),
        (e.CedulaJuridicaDuplicadaError("cedula juridica duplicada"),409),
        (e.NombreCategoriaDuplicadoError("nombre de categoria duplicado"),409),
        (e.UsuarioNoAutorizadoError("no es el propietario"), 403),
        (e.OrganizacionNoAutorizadaError("no autorizada"), 422),
        (e.CategoriaInactivaError("inactiva"), 422),
        (e.CantidadInvalidaError("cantidad"), 422),
        (e.FechaLimiteInvalidaError("fecha"), 422),
        (e.RolOrganizacionIncompatibleError("rol"), 422),
        (e.FechaAcordadaInvalidaError("fecha"), 422),
        (e.ErrorNegocio("generico"), 422),
        (NotFound("no encontrado"), 404),
        (ValidationError({"alimento": ["Este campo es requerido."]}),400),
        (ZeroDivisionError("detalle interno"), 500),
    ],
)
def test_cada_excepcion_produce_problem_details(
    excepcion,
    codigo,
):
    respuesta = responder_con(excepcion)
    cuerpo = respuesta.content.decode()

    assert respuesta.status_code == codigo
    assert respuesta["Content-Type"] == "application/problem+json"
    assert respuesta.data["status"] == codigo
    assert respuesta.data["instance"] == "/api/v1/x"
    assert "Traceback" not in cuerpo


def test_error_interno_no_expone_detalles():
    respuesta = responder_con(
        ZeroDivisionError("detalle interno")
    )

    assert "detalle interno" not in respuesta.content.decode()


def test_validacion_lista_los_campos_invalidos():
    respuesta = responder_con(
        ValidationError(
            {"alimento": ["requerido"]}
        )
    )

    assert "alimento" in respuesta.data["errores"]