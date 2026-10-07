from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView


class VistaSalud(APIView):

    @extend_schema(
        operation_id="consultar_salud",
        summary="Consultar estado de la API",
        description=(
            "Verifica que la API de AlimentaCR se encuentre disponible."
        ),
        responses={
            200: inline_serializer(
                name="SaludResponse",
                fields={
                    "status": serializers.CharField(),
                },
            ),
        },
        auth=[],
    )
    def get(self, request):
        return Response({
            "status": "UP"
        })