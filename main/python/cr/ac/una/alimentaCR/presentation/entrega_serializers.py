from rest_framework import serializers


CAMPOS_COORDINACION = (
    "fecha_acordada",
    "lugar",
    "observaciones",
)


class CoordinarEntregaRequestSerializer(serializers.Serializer):
    """
    DTO de entrada para coordinar una Entrega (PATCH, Proceso 5).

    Todos los campos de coordinacion son opcionales, pero debe venir
    al menos uno. La identidad del usuario se obtiene del JWT.
    """

    fecha_acordada = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    lugar = serializers.CharField(
        max_length=250,
        required=False,
        allow_null=True,
    )

    observaciones = serializers.CharField(
        max_length=500,
        required=False,
        allow_null=True,
    )

    # Bloqueo optimista: version de la entrega que leyo el cliente. Es
    # opcional; si se envia y ya no coincide, la API responde 409.
    version = serializers.IntegerField(
        required=False,
        min_value=0,
    )

    def validate(self, datos):
        if not any(
            campo in datos
            for campo in CAMPOS_COORDINACION
        ):
            raise serializers.ValidationError(
                "Debe enviar al menos uno de: "
                "fecha_acordada, lugar u observaciones."
            )

        return datos


class EntregaResponseSerializer(serializers.Serializer):
    """DTO de salida de una Entrega."""

    id_entrega = serializers.IntegerField()

    id_solicitud = serializers.IntegerField(
        source="solicitud_id"
    )

    fecha_creacion = serializers.DateTimeField()

    fecha_acordada = serializers.DateTimeField(
        allow_null=True
    )

    lugar = serializers.CharField(
        allow_null=True
    )

    observaciones = serializers.CharField(
        allow_null=True
    )

    confirmacion_donante = serializers.BooleanField()

    confirmacion_beneficiario = serializers.BooleanField()

    estado = serializers.CharField()

    version = serializers.IntegerField(
        help_text=(
            "Version del registro (bloqueo optimista). Envielo en el "
            "PATCH para detectar modificaciones simultaneas."
        )
    )