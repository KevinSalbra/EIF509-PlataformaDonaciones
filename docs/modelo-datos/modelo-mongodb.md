## Diseño del subdominio MongoDB — Bitácora de eventos

### Contexto

AlimentaCR utiliza una arquitectura de **persistencia políglota**: PostgreSQL almacena el núcleo transaccional del sistema (usuarios, organizaciones, donaciones, solicitudes, entregas), mientras que **MongoDB almacena la bitácora de eventos**, es decir, el historial de acciones ocurridas sobre esas entidades.

```
                  Aplicación
                      │
             ┌────────┴────────┐
             │                 │
             ▼                 ▼
        PostgreSQL          MongoDB
     (alimentacr)      (alimentacr_bitacora)
             │                 │
      Datos principales    Colección: eventos
      (estado actual)      (historial de acciones)
```

- **PostgreSQL** responde: *"¿Cuál es el estado actual de la donación 184?"*
- **MongoDB** responde: *"¿Qué ocurrió con la donación 184 y quién hizo cada acción?"*

### Colección: `eventos`

| Campo         | Tipo      | Descripción                                          |
|---------------|-----------|------------------------------------------------------|
| `_id`         | ObjectId  | Identificador único del evento, generado por MongoDB |
| `tipo_evento` | String    | Acción que ocurrió                                   |
| `fecha_hora`  | Date      | Momento en que ocurrió el evento                     |
| `usuario_id`  | Integer   | Identificador del usuario que realizó la acción      |
| `entidad`     | String    | Tipo de entidad afectada                             |
| `entidad_id`  | Integer   | Identificador de la entidad afectada                 |
| `datos`       | Object    | Información adicional específica del evento          |

### Tipos de evento registrados

| Módulo         | Eventos                                                         |
|----------------|-----------------------------------------------------------------|
| Organizaciones | `ORGANIZACION_REGISTRADA`, `ORGANIZACION_APROBADA`              |
| Donaciones     | `DONACION_PUBLICADA`, `DONACION_ASIGNADA`                       |
| Solicitudes    | `SOLICITUD_CREADA`, `SOLICITUD_APROBADA`, `SOLICITUD_RECHAZADA` |
| Entregas       | `ENTREGA_PROGRAMADA`, `ENTREGA_CONFIRMADA`, `ENTREGA_CANCELADA` |

## Justificación de diseño

### ¿Cómo se lee el dato el 90 % del tiempo?

La bitácora se consulta principalmente para revisar el **historial de acciones sobre una entidad específica** (una donación, solicitud o entrega puntual). También se usa para consultar las acciones realizadas por un usuario durante un período determinado.

Por esto, los índices de la colección están orientados a esos dos patrones de consulta: `entidad + entidad_id` (historial de un registro) y `usuario_id` (historial de un usuario), además de `fecha_hora` para ordenar cronológicamente y `tipo_evento` para filtrar por tipo de acción.

### ¿Cuánto puede crecer?

La colección crece de forma **continua e ilimitada**: cada operación relevante del sistema genera un nuevo evento. A diferencia de las entidades principales en PostgreSQL, los eventos históricos **no se actualizan**, solo se agregan nuevos documentos conforme ocurren acciones en la plataforma.

**Decisión:** cada evento se almacena como un **documento independiente**, nunca embebido dentro de otra entidad (por ejemplo, no se guarda un arreglo de eventos dentro del documento de una donación), ya que ese arreglo crecería sin límite y degradaría el rendimiento.

### ¿Quién más lo necesita?

El principal consumidor de la bitácora es el **administrador de AlimentaCR**, quien la utiliza para dar seguimiento a las operaciones realizadas dentro de la plataforma.

## Qué se incrusta y qué se referencia

### Se incrusta: `datos`

El campo `datos` se incrusta porque es información **propia del evento**, que varía según el tipo de acción y no tiene sentido normalizar en una colección aparte. Ejemplos:

```json
"datos": {
  "fecha_entrega": "2026-08-20",
  "observacion": "Entrega recibida correctamente"
}
```

```json
"datos": {
  "motivo": "La organización ya no requiere la donación"
}
```

### Se referencia: `usuario_id` y `entidad_id`

Se referencian en lugar de incrustarse porque la información completa de los usuarios y de las entidades afectadas **pertenece a PostgreSQL**. La bitácora solo necesita identificar *quién* realizó la acción y *sobre qué registro*, sin duplicar el resto de los datos (nombre de usuario, detalles completos de la donación, etc.). Duplicar esa información en cada evento generaría redundancia y riesgo de inconsistencia si el dato original cambia en PostgreSQL.

## Ejemplos de documentos

**Donación publicada**
```json
{
  "tipo_evento": "DONACION_PUBLICADA",
  "fecha_hora": "2026-08-17T18:30:00Z",
  "usuario_id": 25,
  "entidad": "DONACION",
  "entidad_id": 184,
  "datos": {
    "cantidad": 50,
    "categoria_id": 3
  }
}
```

**Solicitud creada**
```json
{
  "tipo_evento": "SOLICITUD_CREADA",
  "fecha_hora": "2026-08-18T11:20:00Z",
  "usuario_id": 12,
  "entidad": "SOLICITUD",
  "entidad_id": 72,
  "datos": {
    "categoria_id": 3,
    "cantidad_solicitada": 20
  }
}
```

**Entrega confirmada**
```json
{
  "tipo_evento": "ENTREGA_CONFIRMADA",
  "fecha_hora": "2026-08-19T14:45:00Z",
  "usuario_id": 12,
  "entidad": "ENTREGA",
  "entidad_id": 56,
  "datos": {
    "donacion_id": 184,
    "observacion": "Entrega recibida correctamente"
  }
}
```

## Índices

| Índice                   | Campos                      | Propósito                                        |
|--------------------------|-----------------------------|--------------------------------------------------|
| `idx_fecha_hora`         |`fecha_hora: -1`             | Listar eventos en orden cronológico              |
| `idx_usuario_id`         | `usuario_id: 1`             | Consultar acciones de un usuario                 |
| `idx_entidad_entidad_id` | `entidad: 1, entidad_id: 1` | Consultar el historial de una entidad específica |
| `idx_tipo_evento`        | `tipo_evento: 1`            | Filtrar eventos por tipo de acción               |

## Inicialización automática

La base de datos, la colección, los índices y los datos de ejemplo se crean automáticamente al levantar el contenedor por primera vez, mediante los scripts en `database/mongodb/init/`:

- `01_init.js`: crea la colección `eventos` y sus índices.
- `02_seed.js`: inserta los eventos de ejemplo (solo si la colección está vacía).

Esto permite que cualquier integrante del equipo obtenga el entorno completo con un solo comando:

```bash
docker compose up
```