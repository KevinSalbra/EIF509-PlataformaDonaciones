from rest_framework import serializers


class AceptarSolicitudRequestSerializer(serializers.Serializer):
    """
    DTO de entrada para el Proceso #1 (aceptar solicitud).

    Es el equivalente en DRF a un record de entrada con Bean
    Validation en Java: valida formato antes de que el dato llegue al
    servicio de negocio (id_usuario debe ser un entero positivo). No
    valida reglas de negocio -- eso es responsabilidad exclusiva de
    SolicitudService.
    """

    id_usuario = serializers.IntegerField(min_value=1)


class EntregaResponseSerializer(serializers.Serializer):
    """
    DTO de salida para el Proceso #1.

    Expone unicamente los campos que el exterior necesita conocer de
    la Entrega creada.
    """

    id_entrega = serializers.IntegerField()
    id_solicitud = serializers.IntegerField(source="solicitud_id")
    estado = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()


class PublicarDonacionRequestSerializer(serializers.Serializer):
    """
    DTO de entrada para el Proceso #2 (publicar donacion).

    Valida el formato de los datos antes de que lleguen al servicio
    de negocio. Las reglas propias del dominio permanecen en
    DonacionService.
    """

    id_organizacion = serializers.IntegerField(min_value=1)

    id_categoria = serializers.IntegerField(min_value=1)

    alimento = serializers.CharField(
        max_length=150,
        allow_blank=False,
    )

    descripcion = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    cantidad = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    unidad_medida = serializers.ChoiceField(
        choices=[
            "KILOGRAMO",
            "GRAMO",
            "LITRO",
            "MILILITRO",
            "UNIDAD",
            "PAQUETE",
            "CAJA",
        ]
    )

    fecha_limite_retiro = serializers.DateField()


class DonacionResponseSerializer(serializers.Serializer):
    """
    DTO de salida para el Proceso #2 (publicar donacion).

    Expone los datos necesarios de la Donacion creada sin enviar
    directamente todos los detalles internos del modelo al cliente.
    """

    id_donacion = serializers.IntegerField()

    id_organizacion = serializers.IntegerField(
        source="organizacion_donante_id"
    )

    id_categoria = serializers.IntegerField(
        source="categoria_id"
    )

    alimento = serializers.CharField()

    descripcion = serializers.CharField(
        allow_null=True
    )

    cantidad = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    unidad_medida = serializers.CharField()

    fecha_publicacion = serializers.DateTimeField()

    fecha_limite_retiro = serializers.DateField()

    estado = serializers.CharField()