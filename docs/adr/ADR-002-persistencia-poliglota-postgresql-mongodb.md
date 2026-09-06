ADR-002 · Persistencia políglota: PostgreSQL para el núcleo transaccional y MongoDB para la bitácora de eventos

Estado

Aceptada

Fecha: 24/08/2026
Responsables: Kevin Salazar Bravo y Kimberley Gómez Quesada

Contexto

El Laboratorio 2 del curso requiere construir la capa de datos completa de AlimentaCR combinando dos modelos de persistencia: un núcleo relacional que garantice consistencia y transacciones para las entidades principales del dominio (organizaciones, usuarios, donaciones, solicitudes, entregas), y una parte con naturaleza documental que registre el historial de acciones ocurridas sobre esas entidades.

La mayoría de las operaciones de AlimentaCR (publicar una donación, aceptar una solicitud, confirmar una entrega) requieren integridad referencial estricta, restricciones de unicidad y validaciones a nivel de base de datos, características propias de un modelo relacional normalizado. Sin embargo, el sistema también necesita conservar un registro histórico de qué ocurrió, cuándo y quién lo hizo sobre cada entidad, un dato que crece de forma continua, no se actualiza una vez escrito, y cuya estructura interna puede variar según el tipo de evento (los datos relevantes de una entrega confirmada no son los mismos que los de una solicitud rechazada).

Intentar modelar este historial dentro del esquema relacional implicaría tablas de auditoría con columnas poco flexibles, o bien un esquema entidad-atributo-valor que complicaría las consultas y perdería las ventajas de un modelo documental para este caso de uso puntual.

Decisión

Se utilizará una arquitectura de persistencia políglota compuesta por:

PostgreSQL como base de datos relacional principal, para el núcleo transaccional del sistema: organizaciones, usuarios, categorías, donaciones, solicitudes y entregas. El esquema se administra mediante migraciones versionadas con Flyway, en tercera forma normal, con restricciones (CHECK, UNIQUE, FK) e índices justificados según los patrones de consulta de cada tabla.

Flyway se establece como la fuente de verdad del esquema relacional. Los modelos ubicados en `data/models/` mapean las tablas creadas por Flyway y utilizan `managed = False` para evitar que Django intente administrarlas. Cuando se modifique el esquema, primero deberá crearse una nueva migración Flyway y luego actualizarse el modelo Django correspondiente. `inspectdb` podrá utilizarse únicamente como herramienta de verificación del mapeo.

MongoDB como base de datos documental, exclusivamente para la bitácora de eventos del sistema: una única colección, eventos, que registra el historial de acciones (tipo_evento, fecha_hora, usuario_id, entidad, entidad_id, datos) ocurridas sobre las entidades administradas en PostgreSQL.

Ambas bases de datos se ejecutan mediante Docker Compose, permitiendo levantar el entorno completo con un solo comando. La colección eventos, sus índices y los datos de ejemplo se inicializan automáticamente mediante scripts en database/mongodb/init/, siguiendo el mismo principio de reproducibilidad que las migraciones de Flyway aplican sobre PostgreSQL.

El diseño de la colección eventos (justificación de qué se incrusta y qué se referencia) se documenta por separado en docs/modelo-datos/modelo-mongodb.md.

Alternativas consideradas

Registrar el historial únicamente en PostgreSQL (tabla de auditoría relacional)

Consistía en crear una tabla evento con columnas fijas o un esquema entidad-atributo-valor para almacenar los datos variables de cada tipo de evento.

No fue seleccionada porque los eventos de AlimentaCR tienen estructuras distintas según el tipo de acción (una entrega confirmada registra una observación, una solicitud rechazada registra un motivo, una donación publicada registra cantidad y categoría), lo que en un modelo relacional obligaría a usar columnas nulas en la mayoría de los casos o una tabla de atributos genérica difícil de consultar y mantener.

No usar dos bases de datos (mantener todo en PostgreSQL sin bitácora estructurada)

Consistía en no implementar un registro de eventos, o registrar únicamente cambios de estado mediante columnas de auditoría simples (fecha_actualizacion, actualizado_por) en cada tabla.

No fue seleccionada porque el objetivo del laboratorio es implementar explícitamente un subdominio documental en MongoDB, y porque un historial completo de acciones (no solo el último cambio) es un requisito real del seguimiento administrativo que se busca ofrecer en AlimentaCR.

PostgreSQL para el núcleo transaccional y MongoDB para la bitácora de eventos

Esta fue la alternativa seleccionada. Permite que cada base de datos se use según su fortaleza: PostgreSQL garantiza integridad y consistencia donde el sistema lo requiere, mientras que MongoDB permite almacenar documentos con estructura variable sin necesidad de migrar el esquema cada vez que se agrega un nuevo tipo de evento.

Dentro de MongoDB, se decidió referenciar (no incrustar) los identificadores de usuario y de la entidad afectada (usuario_id, entidad_id), en lugar de duplicar la información completa de esos registros. Esto evita inconsistencias si el dato original cambia en PostgreSQL, y es coherente con el hecho de que la bitácora es consultada principalmente por entidad_id o usuario_id, no como un listado que requiera mostrar de forma inmediata todos los datos del usuario u organización involucrados.

Consecuencias

Positivas

Cada base de datos se utiliza según sus fortalezas: consistencia transaccional en PostgreSQL, flexibilidad documental en MongoDB.

Agregar nuevos tipos de evento (por ejemplo, un nuevo estado de entrega) no requiere migraciones de esquema en MongoDB, solo ajustar el contenido del campo datos.

La colección eventos puede crecer indefinidamente sin afectar el rendimiento ni el diseño de las tablas principales en PostgreSQL.

El historial de acciones queda desacoplado del estado actual: PostgreSQL puede optimizarse para consultas de estado, y MongoDB para consultas de auditoría.

Docker Compose permite levantar ambas bases de datos, con su estructura, índices y datos de ejemplo, mediante un solo comando, favoreciendo la reproducibilidad del entorno para cualquier integrante del equipo.

Negativas

El equipo debe mantener y comprender dos motores de base de datos distintos, con sus propios lenguajes de consulta, herramientas de administración y mecanismos de respaldo.

No existe integridad referencial entre usuario_id / entidad_id en MongoDB y las tablas correspondientes en PostgreSQL; la consistencia entre ambas bases depende de que la aplicación escriba correctamente en ambos lados, no de una restricción de base de datos.

Las pruebas y los datos de ejemplo deben mantenerse coordinados manualmente entre ambos sistemas, ya que los identificadores usados en los seeds de MongoDB deben corresponder a registros reales en PostgreSQL para que la bitácora sea consistente.

Neutras

La documentación técnica del repositorio debe explicar claramente cuándo un dato pertenece a PostgreSQL y cuándo a MongoDB, para que cualquier persona que se incorpore al proyecto entienda el criterio de separación.

Los comandos de configuración, levantamiento y verificación del entorno incluyen ahora pasos específicos para MongoDB, además de los ya existentes para PostgreSQL y Flyway.

Futuras decisiones sobre qué otras partes del sistema podrían beneficiarse de un modelo documental (por ejemplo, catálogos flexibles o comentarios) deberán evaluarse bajo el mismo criterio aplicado aquí: patrón de lectura, crecimiento esperado y necesidad de compartir el dato con otros componentes.