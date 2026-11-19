import logging

import pymongo
from django.db import connection
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.config.mongodb import obtener_cliente_mongo

logger = logging.getLogger(__name__)


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


class VistaHealth(APIView):
    """
    GET /actuator/health

    Indica si la aplicacion y sus bases de datos estan disponibles. La
    plataforma lo usa para saber si el despliegue funciono.

    Responde solo UP/DOWN, sin detalles internos (A02/A10): el motivo del
    fallo se escribe en el registro, no en la respuesta.
      - 200 {"status": "UP"}    PostgreSQL y MongoDB responden.
      - 503 {"status": "DOWN"}  alguna de las dos no responde.
    """

    authentication_classes = []
    permission_classes = []
    # La plataforma lo consulta con frecuencia: no se limita.
    throttle_classes = []

    @staticmethod
    def _postgres_disponible():
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception:
            logger.exception("Health check: PostgreSQL no responde")
            return False

    @staticmethod
    def _mongo_disponible():
        try:
            # Sin limite, un MongoDB caido bloquearia el health check ~30 s
            # (seleccion de servidor).
            with pymongo.timeout(3):
                obtener_cliente_mongo().admin.command("ping")
            return True
        except Exception:
            logger.exception("Health check: MongoDB no responde")
            return False

    @extend_schema(
        operation_id="actuator_health",
        summary="Health check",
        description="UP si la aplicacion y sus bases de datos responden.",
        responses={
            200: inline_serializer(
                name="HealthUp",
                fields={"status": serializers.CharField()},
            ),
            503: inline_serializer(
                name="HealthDown",
                fields={"status": serializers.CharField()},
            ),
        },
        auth=[],
    )
    def get(self, request):
        disponible = self._postgres_disponible() and self._mongo_disponible()
        return Response(
            {"status": "UP" if disponible else "DOWN"},
            status=200 if disponible else 503,
        )