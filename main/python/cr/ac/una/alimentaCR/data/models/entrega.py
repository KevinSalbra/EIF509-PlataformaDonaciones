from django.db import models


class Entrega(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        FINALIZADA = "FINALIZADA", "Finalizada"
        CANCELADA = "CANCELADA", "Cancelada"

    id_entrega = models.BigAutoField(
        primary_key=True
    )

    solicitud = models.OneToOneField(
        "Solicitud",
        on_delete=models.PROTECT,
        db_column="id_solicitud",
        related_name="entrega"
    )

    fecha_creacion = models.DateTimeField()

    fecha_acordada = models.DateTimeField(
        null=True,
        blank=True
    )

    lugar = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )

    observaciones = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    confirmacion_donante = models.BooleanField()

    confirmacion_beneficiario = models.BooleanField()

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices
    )

    class Meta:
        managed = False
        db_table = "entrega"

    def __str__(self):
        return f"Entrega {self.id_entrega}"