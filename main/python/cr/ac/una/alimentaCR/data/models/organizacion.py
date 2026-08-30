from django.db import models


class Organizacion(models.Model):

    class Tipo(models.TextChoices):
        DONANTE = "DONANTE", "Donante"
        BENEFICIARIA = "BENEFICIARIA", "Beneficiaria"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADA = "APROBADA", "Aprobada"
        RECHAZADA = "RECHAZADA", "Rechazada"
        INACTIVA = "INACTIVA", "Inactiva"

    id_organizacion = models.BigAutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=150
    )

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices
    )

    cedula_juridica = models.CharField(
        max_length=30,
        unique=True
    )

    descripcion = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    direccion = models.CharField(
        max_length=250
    )

    telefono = models.CharField(
        max_length=20
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices
    )

    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "organizacion"

    def __str__(self):
        return self.nombre