from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import EntregaService

from .entrega_serializers import (
    CoordinarEntregaRequestSerializer,
    EntregaResponseSerializer,
)
from .listados import (
    EntregaConsultaSerializer,
    listar_paginado,
    respuesta_paginada,
)
from .permisos import EsRepresentanteOrganizacion, organizacion_de_alcance


class EntregaListaView(APIView):
    """
    GET /api/v1/entregas -> 200, lista de entregas

    Las entregas no se crean por POST: las genera el proceso de aceptar
    una solicitud (POST /api/v1/solicitudes/<id>/entrega).

    Requiere autenticacion: cada usuario ve solo las entregas de su
    organizacion (el administrador ve todas).
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="listar_entregas",
        summary="Listar entregas",
        description=(
            "Obtiene la lista de entregas aplicando los parametros "
            "de consulta disponibles."
        ),
        parameters=[EntregaConsultaSerializer],
        responses={
            200: respuesta_paginada(
                "EntregaPaginadaResponse",
                EntregaResponseSerializer,
            ),
        },
    )
    def get(self, request):
        consulta = EntregaConsultaSerializer(
            data=request.query_params
        )
        consulta.is_valid(raise_exception=True)

        coleccion = EntregaService().listar_entregas(
            orden=consulta.orden(),
            visible_para_organizacion=organizacion_de_alcance(request),
        )

        return listar_paginado(
            request,
            coleccion,
            EntregaResponseSerializer,
        )


class EntregaDetalleView(APIView):
    """
    GET   /api/v1/entregas/<id> -> 200 | 404
    PATCH /api/v1/entregas/<id> -> 200 | 400, 403, 404, 409, 422

    El GET requiere autenticacion y responde 404 si la entrega no
    pertenece a la organizacion del usuario (el administrador ve todas).

    El PATCH expone el Proceso 5: coordinar la entrega.
    La identidad del usuario se obtiene del JWT.
    """

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [EsRepresentanteOrganizacion()]

        return [IsAuthenticated()]

    @extend_schema(
        operation_id="obtener_entrega",
        summary="Obtener entrega",
        description=(
            "Obtiene una entrega mediante su identificador."
        ),
        responses={200: EntregaResponseSerializer},
    )
    def get(self, request, id_entrega: int):
        entrega = EntregaService().obtener_entrega(
            id_entrega,
            visible_para_organizacion=organizacion_de_alcance(request),
        )

        return Response(
            EntregaResponseSerializer(entrega).data
        )

    @extend_schema(
        operation_id="coordinar_entrega",
        summary="Coordinar entrega",
        description=(
            "Actualiza los datos de coordinacion de una entrega. "
            "La identidad del usuario se obtiene del token JWT."
        ),
        request=CoordinarEntregaRequestSerializer,
        responses={200: EntregaResponseSerializer},
    )
    def patch(self, request, id_entrega: int):
        entrada = CoordinarEntregaRequestSerializer(
            data=request.data
        )
        entrada.is_valid(raise_exception=True)

        cambios = dict(
            entrada.validated_data
        )

        entrega = EntregaService().coordinar_entrega(
            id_entrega,
            request.user.id_usuario,
            cambios,
        )

        return Response(
            EntregaResponseSerializer(entrega).data
        )