from rest_framework import serializers


ESTADOS = [
    "ACTIVA",
    "INACTIVA",
]


class CrearCategoriaRequestSerializer(serializers.Serializer):
    """DTO de entrada para registrar una Categoria."""

    nombre = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(
        max_length=250,
        required=False,
        allow_null=True,
        allow_blank=True,
    )


class ActualizarCategoriaRequestSerializer(serializers.Serializer):
    """DTO de entrada para actualizar una Categoria (PUT)."""

    nombre = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(
        max_length=250,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    estado = serializers.ChoiceField(choices=ESTADOS)


class CategoriaResponseSerializer(serializers.Serializer):
    """DTO de salida para Categoria."""

    id_categoria = serializers.IntegerField()
    nombre = serializers.CharField()
    descripcion = serializers.CharField(
        allow_null=True
    )
    estado = serializers.CharField()