"""
Utilidades comunes para las colecciones de la API: paginacion con
metadatos, orden por parametro y validacion de los parametros de
consulta (filtros).
"""
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PaginacionEstandar(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound:
            raise ValidationError({"page": ["Numero de pagina invalido."]})

    def get_paginated_response(self, data):
        paginador = self.page.paginator
        return Response(
            {
                "count": paginador.count,
                "page": self.page.number,
                "page_size": paginador.per_page,
                "total_pages": paginador.num_pages,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


def listar_paginado(request, queryset, serializer_class):
    """Pagina el queryset y devuelve la respuesta con sus metadatos."""
    paginador = PaginacionEstandar()
    pagina = paginador.paginate_queryset(queryset, request)
    return paginador.get_paginated_response(
        serializer_class(pagina, many=True).data
    )


def respuesta_paginada(nombre, serializer_class):
    """
    Define para OpenAPI la estructura de una respuesta paginada.

    No modifica la paginacion real de la API; solamente permite que
    Swagger documente correctamente sus metadatos y resultados.
    """
    return inline_serializer(
        name=nombre,
        fields={
            "count": serializers.IntegerField(),
            "page": serializers.IntegerField(),
            "page_size": serializers.IntegerField(),
            "total_pages": serializers.IntegerField(),
            "next": serializers.URLField(
                allow_null=True,
            ),
            "previous": serializers.URLField(
                allow_null=True,
            ),
            "results": serializer_class(
                many=True,
            ),
        },
    )


class ConsultaListadoSerializer(serializers.Serializer):
    """
    Base de los parametros de consulta de una coleccion. Cada recurso
    declara en `campos_orden` los campos por los que se puede ordenar:
    cualquier otro se rechaza con 400 (asi no se puede ordenar por
    campos internos como la contrasena).
    """

    campos_orden = ()

    ordering = serializers.CharField(required=False)

    def validate_ordering(self, valor):
        campos = [c.strip() for c in valor.split(",") if c.strip()]
        invalidos = [
            c
            for c in campos
            if (c[1:] if c.startswith("-") else c) not in self.campos_orden
        ]
        if not campos or invalidos:
            raise serializers.ValidationError(
                "Orden no valido. Campos permitidos: "
                + ", ".join(self.campos_orden)
                + " (use el prefijo - para orden descendente)."
            )
        return campos

    def orden(self):
        return self.validated_data.get("ordering")


class UsuarioConsultaSerializer(ConsultaListadoSerializer):
    campos_orden = (
        "id_usuario",
        "nombre",
        "correo",
        "fecha_registro",
    )


class OrganizacionConsultaSerializer(ConsultaListadoSerializer):
    campos_orden = (
        "id_organizacion",
        "nombre",
        "tipo",
        "estado",
        "fecha_registro",
    )


class CategoriaConsultaSerializer(ConsultaListadoSerializer):
    campos_orden = (
        "id_categoria",
        "nombre",
        "estado",
    )


class EntregaConsultaSerializer(ConsultaListadoSerializer):
    campos_orden = (
        "id_entrega",
        "fecha_creacion",
        "fecha_acordada",
        "estado",
    )


class SolicitudConsultaSerializer(ConsultaListadoSerializer):
    campos_orden = (
        "id_solicitud",
        "fecha_solicitud",
        "estado",
    )

    estado = serializers.ChoiceField(
        choices=[
            "PENDIENTE",
            "ACEPTADA",
            "RECHAZADA",
            "CANCELADA",
        ],
        required=False,
    )

    id_organizacion = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    id_donacion = serializers.IntegerField(
        min_value=1,
        required=False,
    )


class DonacionConsultaSerializer(ConsultaListadoSerializer):
    campos_orden = (
        "id_donacion",
        "alimento",
        "cantidad",
        "fecha_publicacion",
        "fecha_limite_retiro",
        "estado",
    )

    estado = serializers.ChoiceField(
        choices=[
            "DISPONIBLE",
            "ASIGNADA",
            "ENTREGADA",
            "CANCELADA",
            "VENCIDA",
        ],
        required=False,
    )

    id_categoria = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    id_organizacion = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    por_vencer_en_dias = serializers.IntegerField(
        min_value=1,
        max_value=365,
        required=False,
    )