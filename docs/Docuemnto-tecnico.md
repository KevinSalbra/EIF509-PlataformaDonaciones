# Documento técnico — Modelo de datos de AlimentaCR

## 1. Resumen

AlimentaCR utiliza una arquitectura de **persistencia políglota**: el núcleo transaccional del sistema se modela en **PostgreSQL**, en tercera forma normal, mientras que el historial de acciones del sistema se modela como una colección documental en **MongoDB**. La justificación completa de esta decisión se documenta en [ADR-002](adr/ADR-002-persistencia-poliglota-postgresql-mongodb.md).

- **PostgreSQL** responde: *"¿Cuál es el estado actual de la donación 184?"*
- **MongoDB** responde: *"¿Qué ocurrió con la donación 184 y quién hizo cada acción?"*

El diagrama de la arquitectura completa se encuentra en [`modelo-datos/modelo-mongodb.png`](modelo-datos/modelo-mongodb.png). 
El diagrama entidad-relación de PostgreSQL se encuentra en [`modelo-datos/modelo-relacional.png`](modelo-datos/modelo-relacional.png).

---

## 2. Modelo relacional (PostgreSQL)

### 2.1 Entidades principales

| Tabla          | Responsabilidad                                                      |
|----------------|----------------------------------------------------------------------|
| `organizacion` | Organizaciones donantes y beneficiarias registradas en la plataforma |
| `usuario`      | Personas que representan a una organización y operan el sistema      |
| `categoria`    | Clasificación de los alimentos publicados                            |
| `donacion`     | Alimentos publicados por una organización donante                    |
| `solicitud`    | Solicitudes de una organización beneficiaria sobre una donación      |
| `entrega`      | Coordinación y confirmación de la entrega de una donación asignada   |

### 2.2 Relaciones principales

- Una **organización** tiene muchos **usuarios**; cada usuario pertenece a una sola organización.
- Una **organización donante** publica muchas **donaciones**; cada donación pertenece a una categoría.
- Una **donación** puede recibir muchas **solicitudes**, pero solo una puede ser aceptada.
- Una **solicitud aceptada** genera como máximo una **entrega** (relación 1 a 1, `id_solicitud` es `UNIQUE` en `entrega`).

### 2.3 Decisiones de diseño relevantes

- **Enumeraciones (`ENUM`)** para los estados de cada entidad (`estado_organizacion`, `estado_donacion`, `estado_solicitud`, `estado_entrega`, entre otros), en lugar de campos de texto libre, para garantizar consistencia en los valores permitidos.
- **Restricciones `UNIQUE`** en campos como `cedula_juridica` (organización), `correo` (usuario) e `id_solicitud` (entrega), para evitar duplicidad de registros o relaciones inválidas.
- **Índices compuestos** en las consultas más frecuentes del dominio, por ejemplo `(estado, id_categoria)` en `donacion` y `(id_donacion, estado)` en `solicitud`, orientados a los filtros que la aplicación realiza con mayor frecuencia (donaciones disponibles por categoría, solicitudes pendientes de una donación).
- La entrega se crea **únicamente** a partir de una solicitud aceptada, nunca de forma independiente, lo que se refleja en la relación 1 a 1 obligatoria entre `solicitud` y `entrega`.

El esquema completo, con tipos de dato, restricciones e índices, se encuentra documentado en [`modelo-datos/modelo-relacional.md`](modelo-datos/modelo-relacional.md) y se implementa mediante migraciones versionadas con Flyway en `database/migrations/`.

---

## 3. Subdominio documental (MongoDB)

### 3.1 Qué se modela

La colección `eventos`, dentro de la base `alimentacr_bitacora`, registra el historial de acciones ocurridas sobre las entidades del sistema: organizaciones, donaciones, solicitudes y entregas.

| Campo        | Tipo     | Descripción                                                                   |
|--------------|----------|-------------------------------------------------------------------------------|
| `_id`        | ObjectId | Identificador único del evento                                                |
| `tipo_evento`| String   | Acción que ocurrió (ej. `DONACION_PUBLICADA`)                                 |
| `fecha_hora` | Date     | Momento en que ocurrió el evento                                              |
| `usuario_id` | Integer  | Usuario que realizó la acción (referencia a PostgreSQL)                       |
| `entidad`    | String   | Tipo de entidad afectada (`DONACION`, `SOLICITUD`, `ENTREGA`, `ORGANIZACION`) |
| `entidad_id` | Integer  | Identificador de la entidad afectada (referencia a PostgreSQL)                |
| `datos`      | Object   | Información adicional propia de cada tipo de evento                           |

### 3.2 Decisiones de diseño: incrustar vs. referenciar

**Se incrusta:** el campo `datos`, porque su estructura varía según el tipo de evento y es información propia de ese evento puntual (no se reutiliza en otro lado).

**Se referencia:** `usuario_id` y `entidad_id`, porque la información completa de usuarios y entidades pertenece a PostgreSQL. Duplicarla en cada evento generaría redundancia y riesgo de inconsistencia si el dato original cambia.

Esta decisión se tomó respondiendo tres preguntas de diseño:

1. **¿Cómo se lee el dato el 90 % del tiempo?** Principalmente por entidad específica (`entidad + entidad_id`) o por usuario (`usuario_id`), por lo que los índices de la colección están orientados a esos dos patrones de acceso.
2. **¿Cuánto puede crecer?** De forma continua e ilimitada, ya que cada acción relevante genera un nuevo documento; por eso cada evento es un documento independiente, nunca un arreglo embebido dentro de otra entidad.
3. **¿Quién más lo necesita?** Principalmente el administrador de la plataforma, para dar seguimiento a las operaciones del sistema.

La justificación completa, con ejemplos de documentos, se encuentra en [`modelo-datos/modelo-mongodb.md`](modelo-datos/modelo-mongodb.md).

### 3.3 Índices

| Índice                   | Campos                      | Propósito                                        |
|--------------------------|-----------------------------|--------------------------------------------------|
| `idx_fecha_hora`         | `fecha_hora: -1`            | Listar eventos en orden cronológico              |
| `idx_usuario_id`         | `usuario_id: 1`             | Consultar acciones de un usuario                 |
| `idx_entidad_entidad_id` | `entidad: 1, entidad_id: 1` | Consultar el historial de una entidad específica |
| `idx_tipo_evento`        | `tipo_evento: 1`            | Filtrar eventos por tipo de acción               |

### 3.4 Tipos de evento

| Módulo         | Eventos                                                         |
|----------------|-----------------------------------------------------------------|
| Organizaciones | `ORGANIZACION_REGISTRADA`, `ORGANIZACION_APROBADA`              |
| Donaciones     | `DONACION_PUBLICADA`, `DONACION_ASIGNADA`                       |
| Solicitudes    | `SOLICITUD_CREADA`, `SOLICITUD_APROBADA`, `SOLICITUD_RECHAZADA` |
| Entregas       | `ENTREGA_PROGRAMADA`, `ENTREGA_CONFIRMADA`, `ENTREGA_CANCELADA` |

---

## 4. Inicialización y reproducibilidad

Ambas bases de datos se levantan con Docker Compose mediante un solo comando (`docker compose up -d`):

- **PostgreSQL**: el esquema se crea mediante migraciones versionadas con Flyway (`database/migrations/`).
- **MongoDB**: la colección `eventos`, sus índices y los datos de ejemplo se crean automáticamente al iniciar el contenedor, mediante los scripts `database/mongodb/init/01_init.js` (estructura) y `database/mongodb/init/02_seed.js` (datos de ejemplo).

Esto garantiza que cualquier integrante del equipo pueda reconstruir el entorno completo desde cero, sin pasos manuales adicionales. El detalle de los comandos se encuentra en el `README.md` del repositorio.

---

## 5. Documentos relacionados

| Documento | Contenido |
|---|---|
| [`modelo-datos/modelo-relacional.md`](modelo-datos/modelo-relacional.md) | Esquema PostgreSQL detallado |
| [`modelo-datos/modelo-mongodb.md`](modelo-datos/modelo-mongodb.md) | Diseño detallado de la colección `eventos` |
| [`adr/ADR-002-persistencia-poliglota-postgresql-mongodb.md`](adr/ADR-002-persistencia-poliglota-postgresql-mongodb.md) | Decisión de usar PostgreSQL + MongoDB |
