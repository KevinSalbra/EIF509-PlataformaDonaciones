from django.db import models


class Solicitud(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACEPTADA = "ACEPTADA", "Aceptada"
        RECHAZADA = "RECHAZADA", "Rechazada"
        CANCELADA = "CANCELADA", "Cancelada"

    id_solicitud = models.BigAutoField(
        primary_key=True
    )

    donacion = models.ForeignKey(
        "Donacion",
        on_delete=models.PROTECT,
        db_column="id_donacion",
        related_name="solicitudes"
    )

    organizacion_beneficiaria = models.ForeignKey(
        "Organizacion",
        on_delete=models.PROTECT,
        db_column="id_organizacion_beneficiaria",
        related_name="solicitudes"
    )

    fecha_solicitud = models.DateTimeField()

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices
    )

    observacion = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )
    

    class Meta:
        managed = False
        db_table = "solicitud"

    def __str__(self):
        return f"Solicitud {self.id_solicitud}"