from django.db import models


class Donacion(models.Model):

    class UnidadMedida(models.TextChoices):
        KILOGRAMO = "KILOGRAMO", "Kilogramo"
        GRAMO = "GRAMO", "Gramo"
        LITRO = "LITRO", "Litro"
        MILILITRO = "MILILITRO", "Mililitro"
        UNIDAD = "UNIDAD", "Unidad"
        PAQUETE = "PAQUETE", "Paquete"
        CAJA = "CAJA", "Caja"

    class Estado(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        ASIGNADA = "ASIGNADA", "Asignada"
        ENTREGADA = "ENTREGADA", "Entregada"
        CANCELADA = "CANCELADA", "Cancelada"
        VENCIDA = "VENCIDA", "Vencida"

    id_donacion = models.BigAutoField(
        primary_key=True
    )

    organizacion_donante = models.ForeignKey(
        "Organizacion",
        on_delete=models.PROTECT,
        db_column="id_organizacion_donante",
        related_name="donaciones"
    )

    categoria = models.ForeignKey(
        "Categoria",
        on_delete=models.PROTECT,
        db_column="id_categoria",
        related_name="donaciones"
    )

    alimento = models.CharField(
        max_length=150
    )

    descripcion = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unidad_medida = models.CharField(
        max_length=20,
        choices=UnidadMedida.choices
    )

    fecha_publicacion = models.DateTimeField()

    fecha_limite_retiro = models.DateField()

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices
    )

    class Meta:
        managed = False
        db_table = "donacion"

    def __str__(self):
        return f"{self.alimento} - {self.cantidad} {self.unidad_medida}"