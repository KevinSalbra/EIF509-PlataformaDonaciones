from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import SolicitudService

from .entrega_serializers import EntregaResponseSerializer
from .solicitud_serializers import (
    CrearSolicitudRequestSerializer,
    SolicitudResponseSerializer,
)
from .listados import SolicitudConsultaSerializer, listar_paginado
from .permisos import (
    EsRepresentanteBeneficiaria,
    EsRepresentanteDonante,
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

    def get(self, request, id_solicitud: int):
        solicitud = SolicitudService().obtener_solicitud(
            id_solicitud
        )

        return Response(
            SolicitudResponseSerializer(solicitud).data
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