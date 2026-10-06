from rest_framework import serializers

ROLES = [
    "ADMINISTRADOR",
    "REPRESENTANTE_DONANTE",
    "REPRESENTANTE_BENEFICIARIA",
]

ESTADOS = ["ACTIVO", "INACTIVO"]


class CrearUsuarioRequestSerializer(serializers.Serializer):
    """DTO de entrada para registrar un Usuario (valida solo el formato)."""

    id_organizacion = serializers.IntegerField(min_value=1)
    nombre = serializers.CharField(max_length=150)
    correo = serializers.EmailField(max_length=150)
    contrasena = serializers.CharField(
        min_length=8, max_length=128, write_only=True
    )
    telefono = serializers.CharField(
        max_length=20, required=False, allow_null=True
    )
    rol = serializers.ChoiceField(choices=ROLES)


class ActualizarUsuarioRequestSerializer(serializers.Serializer):
    """DTO de entrada para actualizar un Usuario (PUT)."""

    nombre = serializers.CharField(max_length=150)
    telefono = serializers.CharField(
        max_length=20, required=False, allow_null=True
    )
    rol = serializers.ChoiceField(choices=ROLES)
    estado = serializers.ChoiceField(choices=ESTADOS)


class UsuarioResponseSerializer(serializers.Serializer):
    """
    DTO de salida. Nunca incluye la contrasena (ni su hash).
    """

    id_usuario = serializers.IntegerField()
    id_organizacion = serializers.IntegerField(source="organizacion_id")
    nombre = serializers.CharField()
    correo = serializers.EmailField()
    telefono = serializers.CharField(allow_null=True)
    rol = serializers.CharField()
    estado = serializers.CharField()
    fecha_registro = serializers.DateTimeField()

class LoginRequestSerializer(serializers.Serializer):
    """DTO de entrada para iniciar sesion."""

    correo = serializers.EmailField(max_length=150)
    contrasena = serializers.CharField(max_length=128,write_only=True)