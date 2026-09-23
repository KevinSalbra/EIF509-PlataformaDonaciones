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
    la Entrega creada. La entidad Entrega (el modelo del ORM) nunca
    cruza la frontera del servicio hacia la vista o el cliente HTTP
    tal cual: siempre pasa por este serializer.
    """

    id_entrega = serializers.IntegerField()
    id_solicitud = serializers.IntegerField(source="solicitud_id")
    estado = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()