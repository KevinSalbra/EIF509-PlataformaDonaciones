from rest_framework import serializers


class CrearSolicitudRequestSerializer(serializers.Serializer):
    """DTO de entrada para solicitar una donacion (Proceso 3)."""

    id_donacion = serializers.IntegerField(min_value=1)

    observacion = serializers.CharField(
        max_length=500,
        required=False,
        allow_null=True,
    )


class SolicitudResponseSerializer(serializers.Serializer):
    """DTO de salida de una Solicitud."""

    id_solicitud = serializers.IntegerField()

    id_donacion = serializers.IntegerField(
        source="donacion_id"
    )

    id_organizacion_beneficiaria = serializers.IntegerField(
        source="organizacion_beneficiaria_id"
    )

    fecha_solicitud = serializers.DateTimeField()

    estado = serializers.CharField()

    observacion = serializers.CharField(
        allow_null=True
    )