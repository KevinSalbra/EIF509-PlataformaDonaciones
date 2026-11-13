"""
Registros estructurados (JSON, una linea por evento) para la salida estandar.

La plataforma (Render) captura stdout; con un objeto JSON por linea se pueden
filtrar por nivel, evento, usuario o ruta. No usa dependencias nuevas.

Regla de seguridad: nunca se registran contrasenas ni tokens. Como defensa
adicional, cualquier campo extra cuyo nombre sugiera un secreto se enmascara.
"""
import json
import logging
from datetime import datetime, timezone

# Atributos que logging agrega a todo LogRecord: no son campos "extra".
_ATRIBUTOS_ESTANDAR = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__
) | {"message", "asctime", "taskName"}

_NOMBRES_SENSIBLES = (
    "password", "contrasena", "clave", "token", "secret", "authorization",
)


def _es_sensible(nombre):
    nombre = nombre.lower()
    return any(parte in nombre for parte in _NOMBRES_SENSIBLES)


class JsonFormatter(logging.Formatter):
    """Serializa cada LogRecord como un objeto JSON."""

    def format(self, record):
        registro = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Campos pasados con logger.warning(..., extra={...}).
        for nombre, valor in record.__dict__.items():
            if nombre in _ATRIBUTOS_ESTANDAR or nombre.startswith("_"):
                continue
            registro[nombre] = "***" if _es_sensible(nombre) else valor

        if record.exc_info:
            registro["exception"] = self.formatException(record.exc_info)

        return json.dumps(registro, ensure_ascii=False, default=str)