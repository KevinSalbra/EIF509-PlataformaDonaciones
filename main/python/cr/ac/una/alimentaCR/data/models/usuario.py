from django.db import models


class Usuario(models.Model):

    class Rol(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        REPRESENTANTE_DONANTE = (
            "REPRESENTANTE_DONANTE",
            "Representante donante",
        )
        REPRESENTANTE_BENEFICIARIA = (
            "REPRESENTANTE_BENEFICIARIA",
            "Representante beneficiaria",
        )

    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    id_usuario = models.BigAutoField(
        primary_key=True
    )

    organizacion = models.ForeignKey(
        "Organizacion",
        on_delete=models.PROTECT,
        db_column="id_organizacion",
        related_name="usuarios"
    )

    nombre = models.CharField(
        max_length=150
    )

    correo = models.EmailField(
        max_length=150,
        unique=True
    )

    contrasena = models.CharField(
        max_length=255
    )

    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    rol = models.CharField(
        max_length=40,
        choices=Rol.choices
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices
    )

    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "usuario"

    def __str__(self):
        return self.nombre