from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import CategoriaService

from .categoria_serializers import (
    ActualizarCategoriaRequestSerializer,
    CategoriaResponseSerializer,
    CrearCategoriaRequestSerializer,
)


class CategoriaListaView(APIView):
    """
    GET  /api/v1/categorias -> 200, lista de categorias
    POST /api/v1/categorias -> 201 + Location | 400
    """

    def get(self, request):
        categorias = CategoriaService().listar()

        return Response(
            CategoriaResponseSerializer(
                categorias,
                many=True,
            ).data
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
    """
    GET /api/v1/categorias/<id> -> 200 | 404
    PUT /api/v1/categorias/<id> -> 200 | 400, 404
    """

    def get(self, request, id_categoria: int):
        categoria = CategoriaService().obtener(
            id_categoria
        )

        return Response(
            CategoriaResponseSerializer(categoria).data
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