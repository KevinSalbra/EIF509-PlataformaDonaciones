from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class SolicitudDTO:
    id_solicitud: int
    donacion_id: int
    organizacion_beneficiaria_id: int
    fecha_solicitud: datetime
    estado: str
    observacion: Optional[str]