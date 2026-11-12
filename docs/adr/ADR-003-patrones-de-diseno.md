# ADR-003 · Patrones de diseño aplicados en la lógica de negocio

**Responsables:** Kevin Salazar Bravo y Kimberley Gómez Quesada

## Contexto

AlimentaCR implementa procesos de negocio que involucran validaciones, cambios de estado, consultas, persistencia y coordinación de varias entidades. Entre estos procesos se encuentran la publicación de donaciones, la creación y cancelación de solicitudes, la aceptación de una solicitud, el rechazo de las solicitudes restantes y la generación de una entrega.

Conforme aumentó la cantidad de reglas, mantener toda la lógica directamente en las vistas o concentrarla en métodos extensos habría generado duplicación, acoplamiento con Django REST Framework y dificultad para probar las reglas sin utilizar una base de datos o un cliente HTTP.

También se identificaron necesidades específicas:

- Centralizar los procesos y reglas de negocio.
- Separar las consultas y operaciones de persistencia.
- Representar reglas de publicación y criterios de consulta de forma reutilizable.
- Controlar las transiciones de las solicitudes según su estado.
- Evitar que las operaciones principales expongan directamente entidades ORM.
- Sustituir repositorios por dobles de prueba durante las pruebas unitarias.

Por estas razones, era necesario establecer una organización explícita de responsabilidades dentro de las capas `presentation`, `business` y `data`.

## Decisión

Se utilizará una combinación de los patrones Service Layer, Repository, Specification y State, junto con objetos DTO para separar la coordinación de los procesos, las reglas de negocio, el acceso a datos, las transiciones de estado y los contratos de salida.

### Service Layer

Los servicios ubicados en `business/services/` funcionan como puntos de entrada para los procesos de negocio.

Entre ellos se encuentran:

- `DonacionService`.
- `SolicitudService`.
- `EntregaService`.
- `OrganizacionService`.
- `CategoriaService`.
- `UsuarioService`.
- `AuthService`.

Los servicios coordinan validaciones, autorizaciones, cambios de estado, transacciones, repositorios y registro de eventos. La capa de presentación delega en estos servicios en lugar de implementar directamente las reglas del dominio.

Por ejemplo, `SolicitudService` coordina la aceptación de una solicitud, el rechazo de las solicitudes restantes, la asignación de la donación y la creación de la entrega.

### Repository

Los componentes ubicados en `data/repositories/` encapsulan el acceso a PostgreSQL y MongoDB.

`BaseRepository` proporciona operaciones comunes como:

- Obtener todos los registros.
- Obtener un registro por identificador.
- Guardar una entidad.
- Eliminar una entidad.

Los repositorios específicos incorporan consultas propias de cada entidad, optimizaciones y operaciones especiales. Por ejemplo, `DonacionRepository` utiliza `select_for_update()` cuando se necesita bloquear una donación durante la aceptación concurrente de solicitudes.

Los servicios reciben los repositorios mediante el constructor, lo que permite reemplazarlos por dobles de prueba y probar las reglas de negocio sin depender directamente de la infraestructura.

### Specification

El patrón Specification se utiliza para encapsular reglas de validación y criterios de consulta.

Las especificaciones de publicación de donaciones se encuentran en `business/specifications/donacion_specifications.py`. Entre ellas se incluyen:

- `OrganizacionPuedeDonarSpecification`.
- `CategoriaActivaSpecification`.
- `CantidadPositivaSpecification`.
- `FechaLimiteFuturaSpecification`.

Cada especificación representa una regla independiente que determina si una donación puede publicarse.

Las especificaciones de consulta se encuentran en `business/specifications/consulta_specifications.py`. Estas construyen criterios mediante objetos `Q` de Django y pueden combinarse utilizando operaciones `AND` y `OR`.

Esto permite construir filtros de donaciones y solicitudes sin concentrar todas las condiciones en las vistas o repositorios.

### State

El patrón State se utiliza para controlar el ciclo de vida de las solicitudes.

La implementación se encuentra en:

```text
business/states/solicitud_states.py