from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import SolicitudService

from .entrega_serializers import EntregaResponseSerializer
from .listados import (
    SolicitudConsultaSerializer,
    listar_paginado,
    respuesta_paginada,
)
from .permisos import (
    EsRepresentanteBeneficiaria,
    EsRepresentanteDonante,
)
from .solicitud_serializers import (
    CrearSolicitudRequestSerializer,
    SolicitudResponseSerializer,
)


class SolicitudListaView(APIView):
    """
    GET  /api/v1/solicitudes -> 200, lista de solicitudes
    POST /api/v1/solicitudes -> 201 + Location | 400, 404, 409, 422

    El POST expone el Proceso 3 (solicitar una donacion).
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [EsRepresentanteBeneficiaria()]

        return []

    @extend_schema(
        operation_id="listar_solicitudes",
        summary="Listar solicitudes",
        description=(
            "Obtiene la lista de solicitudes aplicando los filtros, "
            "ordenamiento y parametros de consulta disponibles."
        ),
        parameters=[SolicitudConsultaSerializer],
        responses={
            200: respuesta_paginada(
                "SolicitudPaginadaResponse",
                SolicitudResponseSerializer,
            ),
        },
        auth=[],
    )
    def get(self, request):
        consulta = SolicitudConsultaSerializer(
            data=request.query_params
        )
        consulta.is_valid(raise_exception=True)
        datos = consulta.validated_data

        coleccion = SolicitudService().listar_solicitudes(
            estado=datos.get("estado"),
            id_organizacion=datos.get("id_organizacion"),
            id_donacion=datos.get("id_donacion"),
            orden=consulta.orden(),
        )

        return listar_paginado(
            request,
            coleccion,
            SolicitudResponseSerializer,
        )

    @extend_schema(
        operation_id="crear_solicitud",
        summary="Crear solicitud",
        description=(
            "Crea una solicitud sobre una donacion. "
            "La identidad del usuario beneficiario se obtiene "
            "del token JWT."
        ),
        request=CrearSolicitudRequestSerializer,
        responses={201: SolicitudResponseSerializer},
    )
    def post(self, request):
        entrada = CrearSolicitudRequestSerializer(
            data=request.data
        )
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        solicitud = SolicitudService().crear_solicitud(
            id_donacion=datos["id_donacion"],
            id_usuario=request.user.id_usuario,
            observacion=datos.get("observacion"),
        )

        respuesta = Response(
            SolicitudResponseSerializer(solicitud).data,
            status=status.HTTP_201_CREATED,
        )

        respuesta["Location"] = request.build_absolute_uri(
            reverse(
                "solicitud_detalle",
                args=[solicitud.id_solicitud],
            )
        )

        return respuesta


class SolicitudDetalleView(APIView):
    """
    GET    /api/v1/solicitudes/<id> -> 200 | 404
    DELETE /api/v1/solicitudes/<id> -> 204 | 403, 404, 409

    El DELETE expone el Proceso 4: cancelar una solicitud pendiente
    (cancelacion logica: el estado pasa a CANCELADA).
    """

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [EsRepresentanteBeneficiaria()]

        return []

    @extend_schema(
        operation_id="obtener_solicitud",
        summary="Obtener solicitud",
        description=(
            "Obtiene una solicitud mediante su identificador."
        ),
        responses={200: SolicitudResponseSerializer},
        auth=[],
    )
    def get(self, request, id_solicitud: int):
        solicitud = SolicitudService().obtener_solicitud(
            id_solicitud
        )

        return Response(
            SolicitudResponseSerializer(solicitud).data
        )

    @extend_schema(
        operation_id="cancelar_solicitud",
        summary="Cancelar solicitud",
        description=(
            "Cancela una solicitud pendiente. La identidad del "
            "usuario se obtiene del token JWT."
        ),
        request=None,
        responses={204: None},
    )
    def delete(self, request, id_solicitud: int):
        SolicitudService().cancelar_solicitud(
            id_solicitud,
            request.user.id_usuario,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class AceptarSolicitudView(APIView):
    """
    POST /api/v1/solicitudes/<id_solicitud>/aceptar
    -> 201 + Location

    Solo un representante donante autenticado puede ejecutar
    el proceso. La identidad del usuario se obtiene del JWT.
    """

    permission_classes = [EsRepresentanteDonante]

    @extend_schema(
        operation_id="aceptar_solicitud",
        summary="Aceptar solicitud",
        description=(
            "Acepta una solicitud y genera la entrega correspondiente. "
            "La identidad del representante donante se obtiene "
            "del token JWT."
        ),
        request=None,
        responses={201: EntregaResponseSerializer},
    )
    def post(self, request, id_solicitud: int):
        entrega = SolicitudService().aceptar_solicitud(
            id_solicitud,
            request.user.id_usuario,
        )

        respuesta = Response(
            EntregaResponseSerializer(entrega).data,
            status=status.HTTP_201_CREATED,
        )

        respuesta["Location"] = request.build_absolute_uri(
            reverse(
                "entrega_detalle",
                args=[entrega.id_entrega],
            )
        )

        return respuesta