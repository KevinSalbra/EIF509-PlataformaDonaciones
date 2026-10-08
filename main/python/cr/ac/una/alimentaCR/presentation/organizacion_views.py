from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import OrganizacionService

from .listados import (
    OrganizacionConsultaSerializer,
    listar_paginado,
    respuesta_paginada,
)
from .organizacion_serializers import (
    ActualizarOrganizacionRequestSerializer,
    CrearOrganizacionRequestSerializer,
    OrganizacionResponseSerializer,
)
from .permisos import EsAdministrador


class OrganizacionListaView(APIView):
    permission_classes = [EsAdministrador]

    """
    GET  /api/v1/organizaciones  -> 200, lista de organizaciones
    POST /api/v1/organizaciones  -> 201 + Location | 400
    """

    @extend_schema(
        operation_id="listar_organizaciones",
        summary="Listar organizaciones",
        description=(
            "Obtiene la lista de organizaciones aplicando los "
            "parametros de consulta disponibles."
        ),
        parameters=[OrganizacionConsultaSerializer],
        responses={
            200: respuesta_paginada(
                "OrganizacionPaginadaResponse",
                OrganizacionResponseSerializer,
            ),
        },
    )
    def get(self, request):
        consulta = OrganizacionConsultaSerializer(
            data=request.query_params
        )
        consulta.is_valid(raise_exception=True)

        coleccion = OrganizacionService().listar(
            orden=consulta.orden()
        )

        return listar_paginado(
            request,
            coleccion,
            OrganizacionResponseSerializer,
        )

    @extend_schema(
        operation_id="crear_organizacion",
        summary="Crear organizacion",
        description="Registra una nueva organizacion.",
        request=CrearOrganizacionRequestSerializer,
        responses={201: OrganizacionResponseSerializer},
    )
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

    @extend_schema(
        operation_id="obtener_organizacion",
        summary="Obtener organizacion",
        description=(
            "Obtiene una organizacion mediante su identificador."
        ),
        responses={200: OrganizacionResponseSerializer},
    )
    def get(self, request, id_organizacion: int):
        organizacion = OrganizacionService().obtener(
            id_organizacion
        )

        return Response(
            OrganizacionResponseSerializer(organizacion).data
        )

    @extend_schema(
        operation_id="actualizar_organizacion",
        summary="Actualizar organizacion",
        description=(
            "Actualiza los datos de una organizacion existente."
        ),
        request=ActualizarOrganizacionRequestSerializer,
        responses={200: OrganizacionResponseSerializer},
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