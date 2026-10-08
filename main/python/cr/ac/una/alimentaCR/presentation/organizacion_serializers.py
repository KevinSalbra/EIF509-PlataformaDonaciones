from rest_framework import serializers


TIPOS = [
    "DONANTE",
    "BENEFICIARIA",
]

ESTADOS = [
    "PENDIENTE",
    "APROBADA",
    "RECHAZADA",
    "INACTIVA",
]


class CrearOrganizacionRequestSerializer(serializers.Serializer):
    """DTO de entrada para registrar una Organizacion."""

    nombre = serializers.CharField(max_length=150)
    tipo = serializers.ChoiceField(choices=TIPOS)
    cedula_juridica = serializers.CharField(max_length=30)
    descripcion = serializers.CharField(
        max_length=500,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    direccion = serializers.CharField(max_length=250)
    telefono = serializers.CharField(max_length=20)


class ActualizarOrganizacionRequestSerializer(serializers.Serializer):
    """DTO de entrada para actualizar una Organizacion (PUT)."""

    nombre = serializers.CharField(max_length=150)
    tipo = serializers.ChoiceField(choices=TIPOS)
    descripcion = serializers.CharField(
        max_length=500,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    direccion = serializers.CharField(max_length=250)
    telefono = serializers.CharField(max_length=20)
    estado = serializers.ChoiceField(choices=ESTADOS)


class OrganizacionResponseSerializer(serializers.Serializer):
    """DTO de salida para Organizacion."""

    id_organizacion = serializers.IntegerField()
    nombre = serializers.CharField()
    tipo = serializers.CharField()
    cedula_juridica = serializers.CharField()
    descripcion = serializers.CharField(
        allow_null=True
    )
    direccion = serializers.CharField()
    telefono = serializers.CharField()
    estado = serializers.CharField()
    fecha_registro = serializers.DateTimeField()