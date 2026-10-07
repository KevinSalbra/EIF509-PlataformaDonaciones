from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import CategoriaService

from .categoria_serializers import (
    ActualizarCategoriaRequestSerializer,
    CategoriaResponseSerializer,
    CrearCategoriaRequestSerializer,
)
from .listados import (
    CategoriaConsultaSerializer,
    listar_paginado,
    respuesta_paginada,
)
from .permisos import EsAdministrador


class CategoriaListaView(APIView):
    permission_classes = [EsAdministrador]

    """
    GET  /api/v1/categorias -> 200, lista de categorias
    POST /api/v1/categorias -> 201 + Location | 400
    """

    @extend_schema(
        operation_id="listar_categorias",
        summary="Listar categorias",
        description=(
            "Obtiene la lista de categorias aplicando los parametros "
            "de consulta disponibles."
        ),
        parameters=[CategoriaConsultaSerializer],
        responses={
            200: respuesta_paginada(
                "CategoriaPaginadaResponse",
                CategoriaResponseSerializer,
            ),
        },
    )
    def get(self, request):
        consulta = CategoriaConsultaSerializer(
            data=request.query_params
        )
        consulta.is_valid(raise_exception=True)

        coleccion = CategoriaService().listar(
            orden=consulta.orden()
        )

        return listar_paginado(
            request,
            coleccion,
            CategoriaResponseSerializer,
        )

    @extend_schema(
        operation_id="crear_categoria",
        summary="Crear categoria",
        description="Registra una nueva categoria de alimentos.",
        request=CrearCategoriaRequestSerializer,
        responses={201: CategoriaResponseSerializer},
    )
    def post(self, request):
        entrada = CrearCategoriaRequestSerializer(
            data=request.data
        )
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        categoria = CategoriaService().crear(
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion"),
        )

        respuesta = Response(
            CategoriaResponseSerializer(categoria).data,
            status=status.HTTP_201_CREATED,
        )

        respuesta["Location"] = request.build_absolute_uri(
            reverse(
                "categoria_detalle",
                args=[categoria.id_categoria],
            )
        )

        return respuesta


class CategoriaDetalleView(APIView):
    permission_classes = [EsAdministrador]

    """
    GET /api/v1/categorias/<id> -> 200 | 404
    PUT /api/v1/categorias/<id> -> 200 | 400, 404
    """

    @extend_schema(
        operation_id="obtener_categoria",
        summary="Obtener categoria",
        description=(
            "Obtiene una categoria mediante su identificador."
        ),
        responses={200: CategoriaResponseSerializer},
    )
    def get(self, request, id_categoria: int):
        categoria = CategoriaService().obtener(
            id_categoria
        )

        return Response(
            CategoriaResponseSerializer(categoria).data
        )

    @extend_schema(
        operation_id="actualizar_categoria",
        summary="Actualizar categoria",
        description=(
            "Actualiza los datos de una categoria existente."
        ),
        request=ActualizarCategoriaRequestSerializer,
        responses={200: CategoriaResponseSerializer},
    )
    def put(self, request, id_categoria: int):
        entrada = ActualizarCategoriaRequestSerializer(
            data=request.data
        )
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        categoria = CategoriaService().actualizar(
            id_categoria=id_categoria,
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion"),
            estado=datos["estado"],
        )

        return Response(
            CategoriaResponseSerializer(categoria).data
        )