from django.db import models


class Categoria(models.Model):

    class Estado(models.TextChoices):
        ACTIVA = "ACTIVA", "Activa"
        INACTIVA = "INACTIVA", "Inactiva"

    id_categoria = models.BigAutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    descripcion = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices
    )

    class Meta:
        managed = False
        db_table = "categoria"

    def __str__(self):
        return self.nombre
    
    