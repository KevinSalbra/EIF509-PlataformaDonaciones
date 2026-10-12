from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EntregaDTO:
    id_entrega: int
    solicitud_id: int
    fecha_creacion: datetime
    confirmacion_donante: bool
    confirmacion_beneficiario: bool
    estado: str