# Documento técnico y de arquitectura de AlimentaCR

## 1. Introducción

AlimentaCR es una plataforma web para gestionar donaciones de alimentos entre organizaciones donantes y beneficiarias.

El sistema permite publicar donaciones, consultar alimentos disponibles, presentar solicitudes, seleccionar una organización beneficiaria y coordinar la entrega correspondiente. Además, conserva una bitácora de las acciones relevantes realizadas durante estos procesos.

Este documento presenta una síntesis de:

- La arquitectura general del sistema.
- El modelo C4.
- Las decisiones arquitectónicas.
- Los modelos de datos relacional y documental.
- Los mecanismos de seguridad.
- La estrategia de despliegue.
- Las pruebas y medidas de calidad.
- Las limitaciones actuales.
- Las lecciones aprendidas durante el desarrollo.

Los documentos especializados del repositorio contienen el detalle completo de cada tema y se enlazan desde las secciones correspondientes.

---

## 2. Alcance del sistema

AlimentaCR cubre los siguientes procesos principales:

- Administración de organizaciones.
- Administración de categorías de alimentos.
- Administración de usuarios vinculados con organizaciones.
- Publicación de donaciones.
- Consulta de donaciones disponibles.
- Creación y cancelación de solicitudes.
- Aceptación de una solicitud.
- Rechazo de las solicitudes restantes.
- Asignación de una donación.
- Generación de una entrega.
- Confirmación o cancelación de una entrega.
- Registro de eventos relevantes en una bitácora.

El sistema distingue tres tipos principales de usuarios:

| Usuario | Responsabilidad |
|---|---|
| Administrador | Gestiona organizaciones, categorías y operaciones administrativas. |
| Representante donante | Publica donaciones y gestiona las solicitudes recibidas. |
| Representante beneficiario | Consulta donaciones, crea o cancela solicitudes y participa en la confirmación de entregas. |

AlimentaCR registra y coordina las operaciones relacionadas con las donaciones, pero no administra el transporte físico, las rutas de distribución, la conservación de los alimentos ni los controles sanitarios.

La definición detallada del dominio se encuentra en la [propuesta de dominio](Propuesta-Dominio.md).

---

## 3. Arquitectura general

AlimentaCR utiliza una arquitectura por capas que separa las responsabilidades de presentación, negocio y acceso a datos.

### 3.1. Capa de presentación

La presentación se divide en dos interfaces:

- Una SPA desarrollada con React para representantes donantes y beneficiarios.
- Un panel administrativo MVC desarrollado con Django Templates.

La API REST utiliza Django REST Framework y proporciona respuestas en formato JSON. Sus responsabilidades incluyen:

- Recibir solicitudes HTTP.
- Validar datos de entrada.
- Autenticar usuarios mediante JWT.
- Aplicar permisos por rol.
- Comprobar restricciones relacionadas con la organización.
- Delegar las operaciones a la capa de negocio.
- Construir las respuestas HTTP.
- Convertir las excepciones en respuestas basadas en Problem Details.

El panel MVC utiliza vistas, formularios y plantillas renderizadas por Django. Su autenticación se mantiene mediante sesiones y sus formularios utilizan protección CSRF.

### 3.2. Capa de negocio

La capa de negocio implementa y coordina los casos de uso del sistema.

Sus responsabilidades incluyen:

- Aplicar reglas del dominio.
- Verificar autorizaciones relacionadas con los recursos.
- Coordinar operaciones transaccionales.
- Administrar cambios de estado.
- Invocar los repositorios.
- Construir resultados mediante DTO.
- Registrar eventos relevantes en la bitácora.

Entre los servicios principales se encuentran:

- `AuthService`.
- `CategoriaService`.
- `DonacionService`.
- `EntregaService`.
- `OrganizacionService`.
- `SolicitudService`.
- `UsuarioService`.

La capa también utiliza patrones como State y Specification para separar reglas y comportamientos que no deben quedar concentrados en las vistas o los modelos.

### 3.3. Capa de datos

La capa de datos contiene:

- Modelos de Django.
- Repositorios relacionales.
- Repositorios documentales.
- Consultas y filtros.
- Operaciones de persistencia.
- Bloqueos para controlar concurrencia.
- Optimizaciones de consultas.

Los modelos de Django representan las tablas de PostgreSQL, pero el esquema relacional no es administrado por las migraciones de Django. Flyway es la fuente de verdad del esquema y de sus cambios versionados.

Los repositorios emplean operaciones como:

- `select_related()` para evitar consultas N+1.
- `select_for_update()` para bloquear registros durante procesos sensibles.
- Consultas filtradas por estado, organización o categoría.
- Inserción de eventos documentales mediante PyMongo.

---

## 4. Modelo C4

La arquitectura se documenta utilizando tres niveles del modelo C4:

| Nivel | Pregunta que responde | Contenido |
|---|---|---|
| Nivel 1: contexto | ¿Quién utiliza el sistema y para qué? | Administrador, representante donante, representante beneficiario y AlimentaCR. |
| Nivel 2: contenedores | ¿Cuáles aplicaciones y almacenes conforman el sistema? | SPA React, aplicación Django, PostgreSQL y MongoDB. |
| Nivel 3: componentes | ¿Cómo se organiza internamente el backend? | Presentación REST, presentación MVC, servicios, componentes de dominio y repositorios. |

No se incluye un diagrama de nivel 4 porque la estructura de paquetes, clases, métodos y pruebas ya proporciona ese grado de detalle en el código fuente.

El modelo completo, junto con sus diagramas y explicaciones, se encuentra en el [modelo C4 de AlimentaCR](arquitectura/modelo-c4.md).

---

## 5. Decisiones de arquitectura

Las decisiones principales se registran mediante Architecture Decision Records o ADR.

| ADR | Decisión |
|---|---|
| [ADR-001](adr/ADR-001-seleccion-stack-backend.md) | Selección de Python, Django y Django REST Framework para el backend. |
| [ADR-002](adr/ADR-002-persistencia-poliglota-postgresql-mongodb.md) | Uso de PostgreSQL para los datos transaccionales y MongoDB para la bitácora. |
| [ADR-003](adr/ADR-003-patrones-de-diseno.md) | Aplicación de patrones como Repository, Service Layer, Specification, State, DTO e inyección de dependencias. |
| [ADR-004](adr/ADR-004-dominio-y-alcance-alimentacr.md) | Definición del dominio, sus límites y los procesos cubiertos por AlimentaCR. |
| [ADR-005](adr/ADR-005-estrategia-autenticacion.md) | Uso de JWT para la API y sesiones para el panel MVC. |
| [ADR-006](adr/ADR-006-plataforma-y-estrategia-de-despliegue.md) | Despliegue mediante Render, MongoDB Atlas, Docker, Gunicorn y Flyway. |

Estos documentos registran el contexto de cada decisión, las alternativas consideradas y sus consecuencias positivas, negativas y neutras.

---

## 6. Modelo de datos

AlimentaCR utiliza persistencia políglota:

- PostgreSQL conserva el estado transaccional actual.
- MongoDB conserva el historial de eventos relevantes.

Esta separación permite que cada tecnología atienda un tipo de información y un patrón de acceso diferente.

PostgreSQL responde preguntas como:

> ¿Cuál es el estado actual de una donación?

MongoDB responde preguntas como:

> ¿Qué acciones ocurrieron sobre una donación y quién realizó cada una?

La justificación completa se encuentra en el [ADR-002](adr/ADR-002-persistencia-poliglota-postgresql-mongodb.md).

### 6.1. Modelo relacional de PostgreSQL

El núcleo transaccional se encuentra normalizado hasta tercera forma normal.

#### Entidades principales

| Tabla | Responsabilidad |
|---|---|
| `organizacion` | Almacena las organizaciones donantes y beneficiarias registradas. |
| `usuario` | Almacena las personas que representan una organización y operan el sistema. |
| `categoria` | Clasifica los alimentos publicados. |
| `donacion` | Representa los alimentos publicados por una organización donante. |
| `solicitud` | Representa las solicitudes realizadas sobre una donación. |
| `entrega` | Registra la coordinación y confirmación de una donación asignada. |

#### Relaciones principales

- Una organización puede tener varios usuarios.
- Cada usuario pertenece a una organización.
- Una organización donante puede publicar varias donaciones.
- Cada donación pertenece a una categoría.
- Una donación puede recibir varias solicitudes.
- Solamente una solicitud puede ser aceptada para una donación.
- Una solicitud aceptada puede generar como máximo una entrega.
- Cada entrega pertenece a una única solicitud.

#### Decisiones de diseño

El modelo utiliza enumeraciones para restringir los estados permitidos de las entidades, evitando valores arbitrarios en campos de texto.

También emplea restricciones `UNIQUE` en datos como:

- La cédula jurídica de una organización.
- El correo de un usuario.
- La solicitud asociada con una entrega.

Los índices se encuentran orientados a los patrones de consulta frecuentes. Entre ellos se incluyen:

- Donaciones por estado y categoría.
- Solicitudes por donación y estado.
- Búsquedas de entidades mediante identificadores únicos.

La entrega no se crea como una entidad independiente. Su creación forma parte del proceso transaccional de aceptación de una solicitud.

El esquema completo se encuentra en el [modelo relacional](modelo-datos/modelo-relacional.md) y se implementa mediante migraciones versionadas dentro de `database/migrations/`.

### 6.2. Modelo documental de MongoDB

MongoDB almacena la colección `eventos` dentro de la base de datos `alimentacr_bitacora`.

Cada documento representa un evento independiente ocurrido sobre una entidad del sistema.

| Campo | Tipo | Descripción |
|---|---|---|
| `_id` | ObjectId | Identificador único del evento. |
| `tipo_evento` | String | Acción registrada, por ejemplo `DONACION_PUBLICADA`. |
| `fecha_hora` | Date | Momento en que ocurrió el evento. |
| `usuario_id` | Integer | Identificador del usuario que realizó la acción. |
| `entidad` | String | Tipo de entidad afectada. |
| `entidad_id` | Integer | Identificador de la entidad afectada. |
| `datos` | Object | Información adicional propia del evento. |

#### Incrustación y referencias

El campo `datos` se incrusta porque:

- Su estructura puede cambiar según el tipo de evento.
- La información pertenece exclusivamente al evento.
- No necesita reutilizarse como una entidad independiente.

Los campos `usuario_id` y `entidad_id` funcionan como referencias lógicas hacia PostgreSQL.

MongoDB no aplica claves foráneas sobre estos campos. La integridad de las operaciones se controla desde la aplicación y las entidades principales continúan almacenadas en PostgreSQL.

#### Patrones de acceso

Los eventos se consultan principalmente:

- Por fecha.
- Por usuario.
- Por tipo de evento.
- Por entidad e identificador de entidad.

Por esta razón, la colección incluye índices como:

| Índice | Campos | Propósito |
|---|---|---|
| `idx_fecha_hora` | `fecha_hora: -1` | Consultar los eventos desde el más reciente. |
| `idx_usuario_id` | `usuario_id: 1` | Consultar las acciones de un usuario. |
| `idx_entidad_entidad_id` | `entidad: 1, entidad_id: 1` | Consultar el historial de una entidad. |
| `idx_tipo_evento` | `tipo_evento: 1` | Filtrar eventos por tipo. |

Cada evento se almacena como un documento independiente. No se utilizan arreglos de eventos dentro de otros documentos porque la bitácora puede crecer continuamente.

El diseño documental completo se encuentra en el [modelo de MongoDB](modelo-datos/modelo-mongodb.md).

### 6.3. Inicialización y reproducibilidad

En el entorno local, PostgreSQL, MongoDB y Flyway se ejecutan mediante Docker Compose.

PostgreSQL se inicializa utilizando las migraciones versionadas ubicadas en:

```text
database/migrations/
```

MongoDB se inicializa utilizando:

```text
database/mongodb/init/01_init.js
database/mongodb/init/02_insertar_datos_prueba.js
```

El primer script crea la colección, el validador y los índices. El segundo agrega los datos de prueba.

Esta configuración permite reconstruir el entorno local mediante:

```bash
docker compose up -d
```

Los comandos y variables requeridas se documentan en el `README.md` del repositorio.

---

## 7. Seguridad

AlimentaCR combina diferentes mecanismos de seguridad según la interfaz utilizada.

### 7.1. Contraseñas

Las contraseñas no se almacenan en texto plano.

El sistema utiliza las funciones de hash proporcionadas por Django para crear y comprobar hashes de contraseña. El valor original de la contraseña no puede recuperarse desde el dato almacenado.

### 7.2. Autenticación de la API REST

La SPA utiliza JSON Web Tokens para consumir los endpoints protegidos.

Después de autenticar las credenciales, el backend emite un token con tiempo de expiración limitado. La SPA lo envía en las solicitudes posteriores mediante el encabezado de autorización.

En cada solicitud autenticada, el backend consulta nuevamente al usuario para verificar que:

- Exista.
- Continúe activo.
- Mantenga las condiciones necesarias para utilizar el sistema.

La implementación actual utiliza tokens de acceso y no incorpora refresh tokens.

### 7.3. Autenticación del panel MVC

El panel administrativo utiliza sesiones de Django.

La sesión conserva únicamente el identificador requerido para reconocer al administrador autenticado. El identificador de sesión se renueva durante la autenticación para reducir el riesgo de fijación de sesión.

Los formularios del panel utilizan la protección CSRF proporcionada por Django.

### 7.4. Autorización

La autorización se aplica mediante:

- Roles de usuario.
- Estado activo del usuario.
- Tipo de organización.
- Pertenencia del usuario a una organización.
- Relación entre el usuario y el recurso solicitado.
- Permisos específicos de cada endpoint.

No es suficiente que un usuario esté autenticado. También debe tener autorización para realizar la operación sobre el recurso correspondiente.

Por ejemplo, un representante donante solamente puede gestionar solicitudes relacionadas con donaciones publicadas por su propia organización.

### 7.5. Comunicaciones y orígenes

En producción, los servicios públicos utilizan HTTPS.

Los orígenes autorizados para consumir la API se configuran mediante CORS. Los hosts y orígenes confiables de Django también se proporcionan mediante configuración externa.

### 7.6. Configuración sensible

Las contraseñas, claves, tokens y cadenas de conexión no deben incluirse en el código fuente ni en la documentación versionada.

La configuración de cada ambiente se proporciona mediante variables de entorno.

El archivo `.env` se utiliza solamente para desarrollo local y permanece excluido del repositorio. El archivo `.env.example` documenta los nombres de las variables requeridas sin contener credenciales reales.

### 7.7. Limitaciones de seguridad

La versión actual no incluye:

- Autenticación multifactor.
- Refresh tokens.
- Lista de revocación de tokens.
- Rotación automática de claves.
- Recuperación automática de contraseñas.
- Integración con un proveedor externo de identidad.

Estas limitaciones se aceptaron debido al alcance académico del proyecto, pero deberán reevaluarse si el sistema aumenta su cantidad de usuarios o su exposición pública.

La decisión completa se documenta en el [ADR-005](adr/ADR-005-estrategia-autenticacion.md).

---

## 8. Despliegue

La estrategia de despliegue separa las aplicaciones y los almacenes de datos.

| Componente | Plataforma |
|---|---|
| SPA React | Render Static Site |
| API REST y panel MVC | Render Web Service |
| PostgreSQL | Servicio administrado de Render |
| MongoDB | MongoDB Atlas |

### 8.1. Backend

El backend se empaqueta mediante Docker.

La imagen contiene:

- El código de Django.
- Las dependencias de Python.
- Gunicorn.
- Flyway.
- Las migraciones SQL.
- El script de arranque.

En producción, Gunicorn ejecuta la aplicación WSGI de Django. No se utiliza el servidor de desarrollo de Django.

### 8.2. Migraciones

Antes de iniciar Gunicorn, el script de arranque ejecuta Flyway.

La secuencia general es:

1. Configurar la conexión con PostgreSQL.
2. Validar el historial de migraciones.
3. Aplicar las migraciones pendientes.
4. Iniciar Gunicorn si las migraciones finalizaron correctamente.

Si una migración falla, el backend no inicia. Esto evita ejecutar la aplicación con un esquema incompleto o incompatible.

### 8.3. Frontend

La SPA se construye mediante React y Vite.

El proceso de construcción genera archivos estáticos HTML, CSS y JavaScript. La dirección pública de la API se proporciona mediante una variable de configuración del entorno.

### 8.4. Diferencias entre ambientes

El entorno local y el de producción comparten:

- El mismo código.
- El mismo modelo de datos.
- Las mismas migraciones Flyway.
- La misma estructura general de configuración.

Sin embargo, utilizan valores independientes para:

- Hosts autorizados.
- Orígenes CORS.
- Conexiones con las bases de datos.
- Claves de firma.
- Dirección pública de la API.
- Configuración de depuración.

La arquitectura física se presenta en el [diagrama de despliegue](arquitectura/diagrama-despliegue.md), mientras que la decisión completa se encuentra en el [ADR-006](adr/ADR-006-plataforma-y-estrategia-de-despliegue.md).

---

## 9. Pruebas y calidad

El proyecto utiliza pruebas automatizadas con `pytest`.

Las pruebas cubren componentes como:

- Organizaciones.
- Categorías.
- Usuarios.
- Donaciones.
- Solicitudes.
- Entregas.
- Autenticación.
- Permisos.
- Servicios de negocio.
- Repositorios.
- Manejo global de excepciones.

### 9.1. Pruebas unitarias

Los servicios pueden recibir repositorios mediante sus constructores. Esto permite sustituir las dependencias reales por dobles de prueba.

De esta manera, las reglas de negocio pueden probarse sin realizar solicitudes HTTP y, cuando corresponde, sin depender de una base de datos real.

### 9.2. Pruebas de integración

Las pruebas de integración verifican la interacción entre:

- Modelos.
- Repositorios.
- Servicios.
- Base de datos.
- Endpoints REST.

Estas pruebas permiten comprobar que los componentes colaboran correctamente y que las operaciones persisten los cambios esperados.

### 9.3. Consultas N+1

Se realizaron pruebas para comparar consultas sin optimización y consultas que utilizan `select_related()`.

La optimización permite recuperar en una misma consulta las relaciones necesarias, como la organización donante y la categoría de una donación, evitando una consulta adicional por cada registro procesado.

### 9.4. Concurrencia

Las operaciones sensibles utilizan transacciones y bloqueos mediante `select_for_update()`.

Esto es especialmente importante durante la aceptación de una solicitud, ya que dos solicitudes no deben ser aceptadas simultáneamente para una misma donación.

### 9.5. Integración continua

El repositorio utiliza GitHub Actions para ejecutar comprobaciones automáticas.

El flujo de integración continua instala las dependencias y ejecuta verificaciones como:

- `manage.py check`.
- Pruebas automatizadas con `pytest`.

Este proceso permite detectar errores antes de integrar cambios en las ramas principales del proyecto.

---

## 10. Flujo arquitectónico principal

Una operación iniciada desde la SPA sigue normalmente este recorrido:

1. El usuario ejecuta una acción en React.
2. React envía una solicitud HTTPS a la API REST.
3. La presentación valida los datos recibidos.
4. El backend autentica al usuario.
5. Los permisos verifican si el usuario puede acceder a la operación.
6. La vista invoca el servicio correspondiente.
7. El servicio aplica las reglas de negocio.
8. El servicio utiliza repositorios para consultar o modificar los datos.
9. PostgreSQL conserva el estado transaccional.
10. MongoDB registra el evento cuando se requiere trazabilidad.
11. El servicio devuelve un DTO o resultado.
12. La presentación construye la respuesta HTTP.
13. React presenta el resultado al usuario.

Las operaciones del panel administrativo utilizan la misma capa de negocio y de datos. La diferencia es que su presentación utiliza formularios, sesiones y plantillas HTML en lugar de JWT y respuestas JSON.

---

## 11. Limitaciones actuales

La versión actual presenta las siguientes limitaciones:

- No administra transporte ni rutas de entrega.
- No verifica las condiciones sanitarias de los alimentos.
- No incorpora geolocalización.
- No envía notificaciones automáticas por correo o mensajería.
- No incluye autenticación multifactor.
- No utiliza refresh tokens.
- No dispone de recuperación automática de contraseñas.
- No incorpora una lista de revocación de JWT.
- No implementa rotación automática de claves.
- Depende de la disponibilidad de Render y MongoDB Atlas.
- Los servicios gratuitos pueden suspenderse después de periodos de inactividad.
- Las migraciones durante el arranque pueden aumentar el tiempo de inicio.
- La configuración de Django depende del entorno desde un archivo compartido, en lugar de emplear módulos separados para desarrollo y producción.
- La persistencia se distribuye entre dos plataformas diferentes.
- El crecimiento continuo de la bitácora requerirá políticas futuras de retención, archivo o eliminación.
- No existe una transacción distribuida entre PostgreSQL y MongoDB.

La ausencia de una transacción distribuida implica que el cambio transaccional en PostgreSQL y el registro documental en MongoDB no forman una única operación atómica entre ambos motores.

---

## 12. Lecciones aprendidas

### 12.1. Separar responsabilidades facilita el mantenimiento

La división entre presentación, negocio y datos evita concentrar validaciones, consultas y procesos en las vistas.

Esta separación también permite probar las reglas de negocio sin depender directamente de HTTP o de detalles de persistencia.

### 12.2. La persistencia políglota debe responder a necesidades concretas

PostgreSQL y MongoDB no se incorporaron para almacenar la misma información de dos maneras diferentes.

PostgreSQL conserva el estado actual y garantiza la integridad transaccional. MongoDB conserva eventos variables orientados a trazabilidad.

Esta decisión aporta flexibilidad, pero también aumenta la complejidad operativa y obliga a mantener dos tecnologías de persistencia.

### 12.3. Las transacciones no son suficientes sin control de concurrencia

La aceptación de solicitudes requiere garantizar que solamente una organización resulte seleccionada.

El uso de transacciones junto con `select_for_update()` permite bloquear la donación durante el proceso y evita resultados inconsistentes ante solicitudes simultáneas.

### 12.4. Los patrones deben resolver problemas reales

Los patrones utilizados se incorporaron para atender responsabilidades concretas:

- Repository separa las consultas y la persistencia.
- Service Layer coordina los casos de uso.
- Specification encapsula reglas reutilizables.
- State organiza las transiciones permitidas.
- DTO controla la información entregada a la presentación.
- La inyección de dependencias facilita las pruebas.

Aplicar un patrón sin una necesidad concreta habría agregado complejidad innecesaria.

### 12.5. Las pruebas unitarias necesitan dependencias sustituibles

Permitir que los servicios reciban repositorios mediante sus constructores facilitó el uso de dobles de prueba.

Esto hizo posible comprobar reglas, excepciones y resultados de forma aislada y rápida.

### 12.6. Automatizar las migraciones mejora la reproducibilidad

Flyway permite mantener un historial ordenado y versionado del esquema.

Su ejecución durante el arranque asegura que la aplicación no se inicie con una versión incompatible de la base de datos. Sin embargo, también significa que un error de migración bloquea el despliegue.

### 12.7. Desarrollo y producción presentan necesidades diferentes

En desarrollo se prioriza la facilidad para ejecutar y depurar los componentes localmente.

En producción se requieren:

- Gunicorn.
- HTTPS.
- Bases de datos administradas.
- Configuración externa.
- Restricciones de hosts y orígenes.
- Manejo seguro de secretos.

Una aplicación que funciona localmente no está necesariamente preparada para ejecutarse en producción.

### 12.8. Mantener dos mecanismos de autenticación agrega complejidad

JWT resulta apropiado para una SPA que consume una API. Las sesiones resultan apropiadas para un panel MVC renderizado en el servidor.

El uso de ambos mecanismos permite atender las características de cada interfaz, pero obliga a documentar y probar dos flujos de autenticación y autorización.

### 12.9. La documentación debe reflejar la implementación real

Los diagramas, ADR y modelos deben mantenerse alineados con el código.

Documentar características que todavía no existen, como refresh tokens o autenticación multifactor, produciría una descripción incorrecta del sistema. Por ello, las capacidades no implementadas se registran como limitaciones o posibles mejoras futuras.

---

## 13. Documentos relacionados

| Documento | Contenido |
|---|---|
| [Propuesta de dominio](Propuesta-Dominio.md) | Procesos, reglas, alcance y limitaciones del dominio. |
| [Modelo C4](arquitectura/modelo-c4.md) | Diagramas de contexto, contenedores y componentes. |
| [Capa de negocio](arquitectura/capa-negocio.md) | Organización y responsabilidades de la lógica de negocio. |
| [Diagrama de despliegue](arquitectura/diagrama-despliegue.md) | Distribución física de los componentes en producción. |
| [Modelo relacional](modelo-datos/modelo-relacional.md) | Diseño detallado de PostgreSQL. |
| [Modelo MongoDB](modelo-datos/modelo-mongodb.md) | Diseño detallado de la colección de eventos. |
| [ADR-001](adr/ADR-001-seleccion-stack-backend.md) | Selección del stack backend. |
| [ADR-002](adr/ADR-002-persistencia-poliglota-postgresql-mongodb.md) | Persistencia políglota. |
| [ADR-003](adr/ADR-003-patrones-de-diseno.md) | Patrones de diseño. |
| [ADR-004](adr/ADR-004-dominio-y-alcance-alimentacr.md) | Dominio y alcance. |
| [ADR-005](adr/ADR-005-estrategia-autenticacion.md) | Autenticación y autorización. |
| [ADR-006](adr/ADR-006-plataforma-y-estrategia-de-despliegue.md) | Plataforma y despliegue. |
| [Laboratorio 6](despliegue/lab6.md) | Configuración y validación del despliegue. |

---

## 14. Conclusión

La arquitectura de AlimentaCR separa las interfaces, las reglas de negocio y la persistencia para mantener responsabilidades claras y facilitar las pruebas.

PostgreSQL conserva el estado transaccional del dominio, mientras que MongoDB proporciona trazabilidad mediante una bitácora documental. La SPA utiliza la API REST con JWT y el panel administrativo utiliza sesiones de Django. El despliegue separa el frontend, el backend y los servicios de persistencia.

Las decisiones adoptadas responden al alcance académico, al tamaño del equipo y a las necesidades actuales del sistema. Las limitaciones identificadas ofrecen una base para evolucionar la seguridad, la observabilidad, el rendimiento y la operación de AlimentaCR en futuras versiones.