from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class DonacionDTO:
    id_donacion: int
    organizacion_donante_id: int
    categoria_id: int
    alimento: str
    descripcion: str
    cantidad: Decimal
    unidad_medida: str
    fecha_publicacion: datetime
    fecha_limite_retiro: date
    estado: str
    dias_restantes: int