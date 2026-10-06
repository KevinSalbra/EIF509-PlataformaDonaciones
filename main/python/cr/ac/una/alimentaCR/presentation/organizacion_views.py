from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .permisos import EsAdministrador
from cr.ac.una.alimentaCR.business.services import OrganizacionService

from .organizacion_serializers import (
    ActualizarOrganizacionRequestSerializer,
    CrearOrganizacionRequestSerializer,
    OrganizacionResponseSerializer,
)

from .listados import OrganizacionConsultaSerializer, listar_paginado

class OrganizacionListaView(APIView):
    permission_classes = [EsAdministrador]
    """
    GET  /api/v1/organizaciones  -> 200, lista de organizaciones
    POST /api/v1/organizaciones  -> 201 + Location | 400
    """

    def get(self, request):
        consulta = OrganizacionConsultaSerializer(data=request.query_params)
        consulta.is_valid(raise_exception=True)
        coleccion = OrganizacionService().listar(orden=consulta.orden())
        return listar_paginado(request, coleccion, OrganizacionResponseSerializer)

    def post(self, request):
        entrada = CrearOrganizacionRequestSerializer(
            data=request.data
        )
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        organizacion = OrganizacionService().crear(
            nombre=datos["nombre"],
            tipo=datos["tipo"],
            cedula_juridica=datos["cedula_juridica"],
            descripcion=datos.get("descripcion"),
            direccion=datos["direccion"],
            telefono=datos["telefono"],
        )

        respuesta = Response(
            OrganizacionResponseSerializer(organizacion).data,
            status=status.HTTP_201_CREATED,
        )

        respuesta["Location"] = request.build_absolute_uri(
            reverse(
                "organizacion_detalle",
                args=[organizacion.id_organizacion],
            )
        )

        return respuesta


class OrganizacionDetalleView(APIView):
    permission_classes = [EsAdministrador]
    """
    GET /api/v1/organizaciones/<id> -> 200 | 404
    PUT /api/v1/organizaciones/<id> -> 200 | 400, 404
    """

    def get(self, request, id_organizacion: int):
        organizacion = OrganizacionService().obtener(
            id_organizacion
        )

        return Response(
            OrganizacionResponseSerializer(organizacion).data
        )

    def put(self, request, id_organizacion: int):
        entrada = ActualizarOrganizacionRequestSerializer(
            data=request.data
        )
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        organizacion = OrganizacionService().actualizar(
            id_organizacion=id_organizacion,
            nombre=datos["nombre"],
            tipo=datos["tipo"],
            descripcion=datos.get("descripcion"),
            direccion=datos["direccion"],
            telefono=datos["telefono"],
            estado=datos["estado"],
        )

        return Response(
            OrganizacionResponseSerializer(organizacion).data
        )