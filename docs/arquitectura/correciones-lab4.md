# Correcciones de la retroalimentación del Laboratorio 4

---

## 1. Introducción

El presente documento describe las correcciones y mejoras realizadas en el proyecto AlimentaCR a partir de la retroalimentación recibida durante la evaluación del Laboratorio 4. Estas modificaciones tienen como propósito fortalecer la consistencia de las operaciones de negocio, mejorar la organización de las responsabilidades entre componentes y reducir el acoplamiento entre las capas de la aplicación.

Las correcciones se concentraron en tres aspectos principales: el manejo de concurrencia en el proceso de aceptación de solicitudes, la aplicación y documentación del patrón de diseño State y la incorporación de objetos de transferencia de datos (DTO) como contratos de salida de los servicios de negocio.

Para cada corrección se presenta el problema identificado, la solución implementada, su justificación técnica y los resultados obtenidos. También se describen las consideraciones arquitectónicas y las limitaciones que permanecen en la implementación actual.

## 2. Corrección 1: Control de concurrencia y consistencia transaccional

### 2.1. Problema identificado

El proceso de aceptación de solicitudes constituye una operación transaccional importante dentro de AlimentaCR, debido a que involucra modificaciones sobre varias entidades relacionadas. Cuando una organización donante acepta una solicitud, el sistema debe actualizar su estado, rechazar las demás solicitudes pendientes asociadas a la misma donación, asignar la donación y generar el registro de entrega correspondiente.

El principal riesgo aparece cuando dos operaciones intentan aceptar solicitudes de una misma donación de manera simultánea. Si ambas consultan inicialmente que la donación está disponible y posteriormente realizan las modificaciones sin una coordinación adecuada, podrían producirse resultados inconsistentes.

Además, una transacción atómica por sí sola no garantiza que las validaciones realizadas mediante lecturas concurrentes se ejecuten sobre información actualizada. Por esta razón, resulta necesario coordinar el acceso a los registros involucrados.

### 2.2. Solución implementada

Se fortaleció el método `_aceptar_solicitud_transaccional()` de `SolicitudService`, utilizando el decorador `@transaction.atomic` de Django para agrupar las operaciones relacionales dentro de una misma transacción.

También se incorporó el método `obtener_por_id_para_actualizar()` en `DonacionRepository`, el cual utiliza `select_for_update()` para adquirir un bloqueo pesimista sobre la donación durante el proceso de aceptación.

El procedimiento implementado sigue este orden:

1. Consultar inicialmente la solicitud que se desea aceptar.
2. Identificar la donación asociada y obtenerla mediante una consulta con bloqueo.
3. Volver a consultar la solicitud después de adquirir el bloqueo.
4. Validar que la solicitud se encuentre en un estado que permita su aceptación.
5. Verificar que el usuario pertenezca a la organización donante propietaria.
6. Comprobar que la donación continúe disponible.
7. Rechazar las demás solicitudes pendientes asociadas a la misma donación.
8. Guardar los cambios de la solicitud aceptada.
9. Actualizar el estado de la donación a `ASIGNADA`.
10. Crear y persistir la entrega correspondiente.

Las operaciones sobre PostgreSQL se ejecutan dentro de la misma transacción. Ante una excepción que provoque su reversión, los cambios relacionales no se confirman parcialmente.

### 2.3. Justificación técnica

Se seleccionó el bloqueo pesimista porque la aceptación de solicitudes representa una operación en la que dos transacciones concurrentes podrían competir por modificar el mismo recurso de negocio.

Mediante `select_for_update()`, una transacción adquiere un bloqueo sobre el registro de la donación y las demás transacciones que intenten obtener un bloqueo incompatible deberán esperar hasta que este sea liberado.

Esta estrategia permite coordinar las decisiones relacionadas con la disponibilidad de la donación. Además, consultar nuevamente la solicitud después de adquirir el bloqueo evita utilizar un estado obtenido antes de que finalizara otra operación concurrente.

Se consideró que las validaciones tradicionales sobre el estado de la donación no eran suficientes por sí solas, debido a que dos procesos podrían leer el mismo estado inicial antes de realizar sus modificaciones.

La combinación de transacciones atómicas y bloqueo pesimista aprovecha las capacidades de PostgreSQL y permite implementar el control de concurrencia mediante los mecanismos proporcionados por Django.

### 2.4. Consideraciones sobre la bitácora en MongoDB

AlimentaCR utiliza PostgreSQL como base de datos transaccional y MongoDB para almacenar los eventos de la bitácora.

El registro del evento de aceptación se realiza fuera de la transacción relacional, después de ejecutar las modificaciones correspondientes en PostgreSQL.

Esta separación responde a que la implementación actual no utiliza una transacción distribuida común entre ambas bases de datos.

En consecuencia, si el registro de la bitácora falla después de confirmarse la operación relacional, los cambios realizados en PostgreSQL no se revierten automáticamente.

Esta limitación corresponde a la estrategia de persistencia políglota adoptada en el proyecto y debe considerarse al evaluar futuras mejoras de confiabilidad.

### 2.5. Resultado de la corrección

La solución fortalece la consistencia del proceso de aceptación y reduce el riesgo de que dos solicitudes asociadas a una misma donación sean aceptadas simultáneamente.

Asimismo, establece un orden explícito para adquirir el bloqueo y validar los estados, evitando tomar decisiones con información potencialmente desactualizada.

## 3. Corrección 2: Aplicación y documentación del patrón State

### 3.1. Contexto

Las solicitudes de AlimentaCR atraviesan diferentes estados durante su ciclo de vida. Las operaciones que pueden ejecutarse sobre una solicitud dependen de su estado actual y de las reglas de negocio establecidas.

Los estados contemplados son:

- `PENDIENTE`
- `ACEPTADA`
- `RECHAZADA`
- `CANCELADA`

Las transiciones entre estos estados deben respetar las restricciones del dominio, evitando operaciones incompatibles con la situación actual de cada solicitud.

### 3.2. Solución implementada

El proyecto utiliza el patrón de diseño State para representar y validar las operaciones relacionadas con los estados de las solicitudes.

En lugar de concentrar todas las condiciones de transición directamente en los métodos de `SolicitudService`, el servicio obtiene el comportamiento correspondiente mediante la función `obtener_estado()`.

Por ejemplo, durante la aceptación de una solicitud se utiliza:

```python
obtener_estado(solicitud.estado).aceptar(solicitud)
```

Para cancelar una solicitud se utiliza:

```python
obtener_estado(solicitud.estado).cancelar(solicitud)
```

Asimismo, cuando se acepta una solicitud, las demás solicitudes pendientes asociadas a la misma donación se procesan mediante la operación `rechazar()` del estado correspondiente.

Estas operaciones permiten delegar las reglas de transición a los componentes encargados de representar el comportamiento de cada estado.

### 3.3. Distribución de responsabilidades

La implementación establece una separación entre los componentes involucrados en el ciclo de vida de las solicitudes.

**Servicio de negocio:** coordina los procesos de aceptación y cancelación, valida autorizaciones, consulta entidades y organiza las operaciones de persistencia.

**Patrón State:** determina si una operación es válida de acuerdo con el estado actual de la solicitud y aplica el comportamiento correspondiente.

**Repositorio:** proporciona los mecanismos necesarios para consultar y persistir las entidades.

**Capa de presentación:** recibe las peticiones HTTP, valida los datos de entrada y construye las respuestas REST.

Esta distribución permite mantener las reglas de transición dentro de la capa de negocio, sin depender de las validaciones realizadas exclusivamente en los endpoints.

### 3.4. Justificación técnica

Se utiliza el patrón State porque el comportamiento de una solicitud cambia según su estado actual.

Una alternativa consistiría en implementar las transiciones mediante múltiples estructuras condicionales dentro de `SolicitudService`. Aunque esta solución podría funcionar inicialmente, aumentaría la complejidad del servicio conforme se incorporaran nuevas reglas o estados.

El patrón State permite encapsular el comportamiento específico de cada estado y separar las reglas de transición de la coordinación general del proceso.

Esto favorece el principio de responsabilidad única, ya que el servicio no necesita concentrar todas las condiciones relacionadas con los estados.

Además, facilita las pruebas unitarias de las transiciones y permite modificar el comportamiento asociado a un estado sin reorganizar completamente los procesos que utilizan dichas reglas.

### 3.5. Resultado de la corrección

La aplicación del patrón State centraliza las reglas de transición de las solicitudes y permite reutilizarlas en distintos procesos de negocio.

La documentación de este comportamiento también facilita comprender cómo se controla el ciclo de vida de las solicitudes y cuál es la responsabilidad de cada componente.

## 4. Corrección 3: Incorporación de DTO y separación de capas

### 4.1. Problema identificado

Durante la evaluación se identificó que algunos servicios de negocio devolvían directamente entidades ORM de Django, aunque la API ya contaba con serializadores de entrada y salida.

Los serializadores permiten validar solicitudes HTTP y transformar los resultados en representaciones JSON. Sin embargo, su existencia no elimina automáticamente el acoplamiento entre los servicios de negocio y las entidades utilizadas para la persistencia.

Devolver directamente modelos ORM implica que los consumidores de los servicios reciben objetos vinculados a la estructura de datos y al comportamiento del framework.

Por esta razón, se consideró necesario establecer contratos de salida más explícitos mediante objetos de transferencia de datos.

### 4.2. Solución implementada

Se incorporaron objetos DTO (*Data Transfer Objects*) para representar los resultados de las operaciones principales de negocio.

Estos objetos se implementaron mediante `dataclass` de Python, utilizando `frozen=True` para impedir la reasignación directa de sus atributos.

Se definieron los siguientes DTO:

- `DonacionDTO`
- `SolicitudDTO`
- `EntregaDTO`

Cada DTO contiene los atributos necesarios para representar la información devuelta por una operación, sin exponer directamente la instancia ORM correspondiente.

Los DTO se encuentran organizados dentro del paquete `business/dto/`.

### 4.3. Modificaciones en DonacionService

En `DonacionService`, el método `publicar_donacion()` fue ajustado para devolver un `DonacionDTO`.

La entidad ORM continúa utilizándose internamente para ejecutar las validaciones y operaciones de persistencia correspondientes.

Una vez almacenada la donación, el servicio construye el DTO que representa el resultado de la operación.

Este cambio permite que la capa de presentación reciba un objeto de salida definido explícitamente por la capa de negocio.

### 4.4. Modificaciones en SolicitudService

En `SolicitudService` se ajustaron los métodos públicos principales para devolver DTO.

| Método | Tipo de retorno |
|---|---|
| `crear_solicitud()` | `SolicitudDTO` |
| `obtener_solicitud()` | `SolicitudDTO` |
| `cancelar_solicitud()` | `SolicitudDTO` |
| `aceptar_solicitud()` | `EntregaDTO` |

Para construir estos objetos se incorporaron métodos internos de conversión, entre ellos:

- `_convertir_solicitud_a_dto()`
- `_convertir_entrega_a_dto()`

También se incorporó `_obtener_solicitud_entidad()` para recuperar una entidad ORM cuando una operación de negocio necesita modificarla.

Esta separación es especialmente importante en `cancelar_solicitud()`, debido a que el patrón State necesita trabajar con una entidad modificable antes de persistir el nuevo estado.

Una vez guardados los cambios, el servicio convierte la entidad resultante a `SolicitudDTO`.

De esta manera, las operaciones internas conservan la capacidad de modificar las entidades, mientras que los métodos públicos principales proporcionan objetos de salida inmutables.

### 4.5. Modificaciones en los listados paginados

Los listados requieren un tratamiento diferente, debido a que las consultas deben conservar los filtros, el ordenamiento y la paginación.

Se mantuvo el método `listar_solicitudes()` para construir el `QuerySet` filtrado mediante Specifications y aplicar el ordenamiento correspondiente.

Adicionalmente, se incorporó `listar_solicitudes_paginadas()`, que coordina la consulta, aplica la paginación y convierte los registros de la página seleccionada a `SolicitudDTO`.

Este procedimiento evita convertir toda la colección antes de aplicar la paginación.

La vista utiliza los DTO obtenidos para construir la respuesta mediante `SolicitudResponseSerializer`.

La estructura de la respuesta paginada conserva los siguientes campos:

- `count`
- `page`
- `page_size`
- `total_pages`
- `next`
- `previous`
- `results`

Esto permite mantener el contrato REST existente y reducir la exposición directa de entidades ORM durante la construcción de los resultados.

### 4.6. Justificación técnica

Se decidió incorporar DTO para establecer contratos de salida explícitos y reducir el acoplamiento entre las entidades de persistencia y los resultados de los servicios de negocio.

Una alternativa era continuar devolviendo directamente entidades ORM. Aunque esto simplifica inicialmente la implementación, también vincula los resultados del servicio con los modelos utilizados por Django para acceder a la base de datos.

Otra alternativa consistía en utilizar diccionarios. Sin embargo, los DTO proporcionan una estructura definida mediante atributos y anotaciones de tipo, lo que facilita comprender la información que devuelve cada operación.

El uso de `@dataclass(frozen=True)` también permite expresar que estos objetos representan resultados y no entidades destinadas a modificarse y persistirse directamente.

En los listados se optó por realizar la conversión después de paginar, con el propósito de evitar cargar innecesariamente todos los registros y conservar las operaciones de filtrado y ordenamiento en PostgreSQL.

Por lo tanto, la solución busca equilibrar la separación de responsabilidades con la compatibilidad de la implementación existente.

### 4.7. Limitaciones arquitectónicas

La incorporación de DTO mejora los contratos de salida de los servicios, pero no elimina completamente las dependencias entre las capas.

Actualmente, `listar_solicitudes()` continúa devolviendo un `QuerySet` para su utilización interna, mientras que `listar_solicitudes_paginadas()` recibe un paginador y el objeto `request` asociados a Django REST Framework.

Esto significa que la capa de negocio todavía conserva una dependencia con componentes utilizados por la presentación en el proceso de paginación.

Como mejora futura, podría definirse un contrato de paginación independiente del framework, mediante parámetros simples y un objeto de resultado paginado que contenga los DTO y sus metadatos.

De esta forma, la presentación sería responsable de interpretar la solicitud HTTP y el servicio recibiría únicamente los parámetros necesarios para realizar la consulta.

### 4.8. Resultado de la corrección

La incorporación de DTO reduce la exposición directa de entidades ORM en los resultados de las operaciones principales de negocio.

También establece una distinción más clara entre las entidades utilizadas para modificar y persistir información y los objetos utilizados para comunicar resultados.

La refactorización permitió conservar los serializadores REST existentes y mantener el comportamiento esperado de los endpoints.

## 5. Validación de las correcciones

### 5.1. Estrategia de validación

Las modificaciones fueron acompañadas por la ejecución de pruebas de negocio, integración y presentación.

La validación contempló aspectos como las reglas de aceptación de solicitudes, la consistencia de las operaciones transaccionales, la compatibilidad de los DTO con los serializadores y la conservación del comportamiento de los endpoints.

También se realizaron pruebas específicas relacionadas con concurrencia y reversión de transacciones.

En los listados se verificó mediante la suite existente que los cambios no alteraran el comportamiento esperado de los filtros, el ordenamiento y las respuestas paginadas.

### 5.2. Ejecución de las pruebas

Una vez integradas las modificaciones, se ejecutó la suite completa del proyecto mediante:

```bash
python -m pytest -v
```

El resultado reportado fue:

```text
205 passed
```

Las 205 pruebas finalizaron correctamente, sin fallos reportados durante esa ejecución.

Este resultado proporciona evidencia de que los cambios realizados mantienen la compatibilidad con los comportamientos cubiertos por la suite.

No obstante, la aprobación de las pruebas no garantiza por sí sola la ausencia de todos los posibles problemas de concurrencia o acoplamiento arquitectónico, por lo que también se requiere considerar la revisión del código y las limitaciones documentadas.

## 6. Componentes involucrados

Los principales componentes relacionados con las correcciones se presentan a continuación.

| Componente | Responsabilidad |
|---|---|
| `SolicitudService` | Procesos de aceptación, creación, consulta, cancelación y listado de solicitudes |
| `DonacionService` | Publicación de donaciones y conversión de resultados a DTO |
| `DonacionRepository` | Consulta de donaciones y bloqueo pesimista |
| `SolicitudRepository` | Consulta y persistencia de solicitudes |
| `business/states/` | Reglas de transición asociadas a los estados de solicitud |
| `business/dto/` | Definición de los objetos de transferencia de datos |
| `solicitud_views.py` | Exposición de los endpoints REST de solicitudes |
| `solicitud_serializers.py` | Validación y representación REST de solicitudes |
| `listados.py` | Validación de consultas y utilidades compartidas de paginación |

## 7. Conclusiones

Las correcciones realizadas a partir de la retroalimentación del Laboratorio 4 permitieron fortalecer aspectos relevantes de la arquitectura y del comportamiento de AlimentaCR.

En primer lugar, la incorporación de bloqueo pesimista y transacciones atómicas mejora el control de concurrencia durante la aceptación de solicitudes, reduciendo el riesgo de inconsistencias cuando existen operaciones simultáneas sobre una misma donación.

En segundo lugar, la aplicación y documentación del patrón State permite centralizar las reglas de transición de las solicitudes y distribuir de manera más clara las responsabilidades entre los componentes de negocio.

Finalmente, la incorporación de DTO establece contratos de salida explícitos para las operaciones principales y reduce el acoplamiento entre los resultados de los servicios y las entidades ORM utilizadas para la persistencia.

Las modificaciones se integraron conservando el comportamiento esperado de la API y fueron verificadas mediante la ejecución de la suite completa, con 205 pruebas aprobadas.

Como oportunidades de mejora futura, se identifican la eliminación de las dependencias del framework REST en los servicios de paginación y el fortalecimiento de los mecanismos de recuperación ante fallos en el registro de eventos de MongoDB.

En conjunto, estas correcciones contribuyen a una implementación más consistente, mantenible y alineada con los principios de separación de responsabilidades establecidos para el proyecto AlimentaCR.