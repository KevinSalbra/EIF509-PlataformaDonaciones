# Laboratorio 5: API REST y Servicios Web

## 1. Introducción

El Laboratorio 5 se centró en implementar y consolidar la API REST de **AlimentaCR**, plataforma destinada a gestionar donaciones de alimentos entre organizaciones donantes y beneficiarias. El objetivo fue exponer los recursos y procesos de negocio del sistema mediante operaciones HTTP, manteniendo la arquitectura por capas establecida en las etapas anteriores.

Se utilizó **Django REST Framework (DRF)** para desarrollar la capa de presentación. Las vistas reciben solicitudes, validan los datos mediante *serializers*, aplican controles de acceso y delegan las operaciones a los servicios de negocio. Así, las reglas del dominio permanecen fuera de las vistas y pueden reutilizarse sin duplicación.

Además de los endpoints, el laboratorio incorporó respuestas de error estandarizadas, consultas con paginación, ordenamiento y filtros, autenticación con JSON Web Tokens (JWT), autorización por roles y documentación OpenAPI con Swagger UI. El trabajo se complementó con pruebas automatizadas y ejecución de integración continua en GitHub Actions.

## 2. Objetivos de la implementación

### 2.1. Objetivo general

Implementar una API REST versionada para AlimentaCR que permita consultar y gestionar sus recursos y ejecutar sus procesos de negocio mediante servicios web, con validación de datos, manejo uniforme de errores, seguridad, documentación y pruebas automatizadas.

### 2.2. Objetivos específicos

- Exponer las operaciones de las entidades Organización, Categoría, Usuario, Donación, Solicitud y Entrega mediante endpoints REST.
- Integrar los endpoints con los servicios de negocio existentes, preservando las responsabilidades de cada capa.
- Estandarizar la validación de solicitudes y la representación de errores mediante códigos HTTP y Problem Details.
- Incorporar paginación, ordenamiento y filtros controlados en los listados de recursos.
- Implementar autenticación JWT y autorización basada en los roles y las restricciones del dominio.
- Documentar las operaciones y sus esquemas mediante OpenAPI y Swagger UI.
- Verificar el comportamiento de la API mediante pruebas automatizadas y un flujo de integración continua.

## 3. Arquitectura e implementación de la API REST

La API se organiza bajo el prefijo **`/api/v1/`**, definido en la configuración de rutas de Django. Este versionado establece una entrada común para los recursos y permite evolucionar el contrato HTTP sin mezclarlo con las rutas administrativas ni con las de documentación.

El recorrido de una petición es el siguiente:

1. El cliente envía una solicitud HTTP al endpoint correspondiente.
2. La vista de DRF recibe la petición; cuando corresponde, se ejecutan la autenticación y la comprobación de permisos.
3. Un serializer valida los datos de entrada o los parámetros de consulta.
4. La vista delega la operación al servicio de negocio responsable.
5. El servicio aplica las reglas del dominio y utiliza los repositorios y modelos necesarios.
6. La vista serializa el resultado y devuelve una respuesta HTTP; si ocurre un error, interviene el manejador global.

Esta distribución evita trasladar las reglas de negocio a la capa de presentación. Los modelos relacionales, la persistencia y varios procesos de negocio fueron desarrollados en laboratorios anteriores; en este laboratorio se construyó o amplió su exposición mediante servicios web.

**Archivos principales:**

- `main/python/cr/ac/una/alimentaCR/config/urls.py`: rutas principales de Django.
- `main/python/cr/ac/una/alimentaCR/presentation/urls_v1.py`: registro de endpoints versionados.
- `main/python/cr/ac/una/alimentaCR/presentation/*_views.py`: vistas HTTP por recurso.
- `main/python/cr/ac/una/alimentaCR/presentation/*_serializers.py` y `presentation/serializers.py`: estructuras y validaciones de entrada y salida.
- `main/python/cr/ac/una/alimentaCR/business/services/`: operaciones y reglas de negocio.
- `main/python/cr/ac/una/alimentaCR/data/repositories/`: acceso a los datos.

## 4. Recursos y endpoints implementados

Los recursos se exponen con métodos HTTP acordes con las operaciones admitidas por el sistema. No se implementó un CRUD irrestricto para todas las entidades: algunas acciones se ejecutan exclusivamente mediante procesos de negocio específicos.

| Recurso | Método | Ruta | Función |
|---|---|---|---|
| Salud | GET | `/api/v1/salud` | Comprobar la disponibilidad de la API. |
| Organizaciones | GET | `/api/v1/organizaciones` | Listar organizaciones. |
| Organizaciones | POST | `/api/v1/organizaciones` | Registrar una organización. |
| Organizaciones | GET | `/api/v1/organizaciones/{id}` | Consultar una organización. |
| Organizaciones | PUT | `/api/v1/organizaciones/{id}` | Actualizar una organización. |
| Categorías | GET | `/api/v1/categorias` | Listar categorías. |
| Categorías | POST | `/api/v1/categorias` | Registrar una categoría. |
| Categorías | GET | `/api/v1/categorias/{id}` | Consultar una categoría. |
| Categorías | PUT | `/api/v1/categorias/{id}` | Actualizar una categoría. |
| Usuarios | GET | `/api/v1/usuarios` | Listar usuarios. |
| Usuarios | POST | `/api/v1/usuarios` | Registrar un usuario. |
| Usuarios | GET | `/api/v1/usuarios/{id}` | Consultar un usuario. |
| Usuarios | PUT | `/api/v1/usuarios/{id}` | Actualizar un usuario. |
| Donaciones | GET | `/api/v1/donaciones` | Listar donaciones. |
| Donaciones | GET | `/api/v1/donaciones/{id}` | Consultar una donación. |
| Donaciones | POST | `/api/v1/donaciones/publicar` | Publicar una donación. |
| Solicitudes | GET | `/api/v1/solicitudes` | Listar solicitudes. |
| Solicitudes | POST | `/api/v1/solicitudes` | Crear una solicitud. |
| Solicitudes | GET | `/api/v1/solicitudes/{id}` | Consultar una solicitud. |
| Solicitudes | DELETE | `/api/v1/solicitudes/{id}` | Cancelar una solicitud pendiente. |
| Solicitudes | POST | `/api/v1/solicitudes/{id}/aceptar` | Aceptar una solicitud y generar una entrega. |
| Entregas | GET | `/api/v1/entregas` | Listar entregas. |
| Entregas | GET | `/api/v1/entregas/{id}` | Consultar una entrega. |
| Entregas | PATCH | `/api/v1/entregas/{id}` | Coordinar una entrega. |
| Autenticación | POST | `/api/v1/auth/login` | Validar credenciales y emitir un JWT. |

En las rutas anteriores, `{id}` representa el identificador del recurso correspondiente. Las rutas de consulta y modificación no tienen necesariamente los mismos permisos: estos se aplican según la operación.

### 4.1. Procesos de negocio expuestos

**Publicar una donación.** El representante de una organización donante envía los datos del alimento, la categoría, la cantidad, la unidad de medida y la fecha límite de retiro. La vista valida la estructura de entrada y llama a `DonacionService`. La organización donante se obtiene de la identidad autenticada, en lugar de confiar en un identificador enviado libremente por el cliente. La creación exitosa devuelve **201 Created** y una cabecera **Location** con la URL del nuevo recurso.

**Crear una solicitud.** Un representante beneficiario solicita una donación disponible mediante `POST /api/v1/solicitudes`. El usuario solicitante se identifica a partir del JWT y `SolicitudService` aplica las restricciones del dominio. La respuesta de creación incluye **201 Created** y **Location**.

**Cancelar una solicitud.** `DELETE /api/v1/solicitudes/{id}` ejecuta una cancelación lógica: la solicitud cambia a estado **CANCELADA** cuando las reglas lo permiten, sin eliminar físicamente el registro. La operación exitosa responde con **204 No Content**.

**Aceptar una solicitud.** `POST /api/v1/solicitudes/{id}/aceptar` permite al representante donante autorizado aceptar una solicitud y generar la entrega correspondiente. Este endpoint reutiliza el proceso transaccional desarrollado previamente: la aceptación y sus cambios relacionados deben respetar las reglas de consistencia del dominio. La entrega generada se devuelve con **201 Created** y **Location**.

**Coordinar una entrega.** `PATCH /api/v1/entregas/{id}` permite actualizar datos de coordinación mediante `EntregaService`, sujeto a las validaciones y permisos correspondientes. Las entregas no se crean mediante un `POST /entregas` independiente: surgen del proceso de aceptación de solicitudes.

## 5. Validación y manejo global de errores

### 5.1. Validación de entrada

Los serializers de DRF comprueban la estructura y los tipos de datos recibidos, los campos obligatorios y las restricciones de formato. Los servicios de negocio mantienen las validaciones propias del dominio, como estados permitidos, disponibilidad, pertenencia a una organización y compatibilidad entre operaciones.

Esta separación distingue dos tipos de responsabilidad: la capa de presentación valida **cómo llega** una petición y la capa de negocio determina **si la operación está permitida** conforme a las reglas del sistema.

### 5.2. Respuestas Problem Details

Se implementó un manejador centralizado en `presentation/exception_handler.py`, basado en **Problem Details (RFC 9457)**. Su propósito es evitar respuestas de error heterogéneas y traducir las excepciones de validación, autenticación, autorización y negocio a un formato común.

La estructura general de una respuesta de error es:

```json
{
  "type": "about:blank",
  "title": "Conflict",
  "status": 409,
  "detail": "Descripción del conflicto de negocio.",
  "instance": "/api/v1/recurso"
}
```

El tipo de contenido utilizado es `application/problem+json`. En errores de validación también puede incorporarse el campo adicional `errores` con el detalle de los campos rechazados.

| Código HTTP | Interpretación en la API |
|---|---|
| 400 Bad Request | Datos o parámetros de entrada inválidos. |
| 401 Unauthorized | Autenticación ausente o credenciales inválidas. |
| 403 Forbidden | Usuario autenticado sin permisos para la operación. |
| 404 Not Found | Recurso solicitado inexistente. |
| 405 Method Not Allowed | Método HTTP no admitido por el endpoint. |
| 409 Conflict | Conflicto con el estado actual o una restricción de negocio. |
| 422 Unprocessable Entity | Operación que incumple una regla del dominio. |
| 500 Internal Server Error | Error interno no controlado, registrado en el log. |

La correspondencia concreta entre excepción y código se mantiene en el mapa de excepciones del manejador global.

## 6. Paginación, ordenamiento y filtros

Los listados se implementaron con una utilidad común en `presentation/listados.py`. El propósito es evitar respuestas excesivamente grandes y ofrecer un contrato uniforme de consulta para las colecciones.

### 6.1. Paginación

La clase `PaginacionEstandar`, basada en `PageNumberPagination`, establece **10 registros por página** de manera predeterminada y admite el parámetro `page_size` con un máximo de **100 registros**. El número de página se solicita mediante `page`.

Una respuesta paginada contiene:

```json
{
  "count": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3,
  "next": "http://localhost:8000/api/v1/donaciones?page=2",
  "previous": null,
  "results": []
}
```

Este JSON es **ilustrativo**: los valores, la URL y el arreglo de resultados dependen de los datos reales de cada consulta.

### 6.2. Ordenamiento

El parámetro `ordering` permite seleccionar uno o varios campos autorizados para ordenar los resultados. Un nombre de campo indica orden ascendente; el prefijo `-` indica orden descendente. Cada recurso define explícitamente sus campos permitidos, de modo que no se expongan campos internos o sensibles como criterios de ordenamiento.

Ejemplo:

```http
GET /api/v1/donaciones?ordering=-fecha_publicacion
```

### 6.3. Filtros y patrón Specification

Las donaciones admiten filtros por `estado`, `id_categoria`, `id_organizacion` y `por_vencer_en_dias`. Las solicitudes admiten `estado`, `id_organizacion` e `id_donacion`. Los parámetros se validan antes de ejecutar la consulta.

Los criterios de consulta se encapsulan en `business/specifications/consulta_specifications.py`. Las clases de Specification generan condiciones `Q` de Django y permiten combinar criterios mediante operadores lógicos **AND** y **OR**. Esta decisión separa la definición de los filtros de la vista HTTP y facilita su reutilización.

Ejemplo de solicitud:

```http
GET /api/v1/donaciones?estado=DISPONIBLE&id_categoria=3&ordering=fecha_limite_retiro&page=1&page_size=10
```

Los identificadores del ejemplo deben corresponder a registros existentes para obtener resultados.

## 7. Autenticación JWT y autorización

### 7.1. Inicio de sesión y emisión del token

Se incorporó `POST /api/v1/auth/login`, que recibe las credenciales del usuario mediante un serializer, las valida a través del servicio correspondiente y devuelve un token JWT cuando la autenticación es correcta.

La respuesta exitosa utiliza la estructura:

```json
{
  "access_token": "<token-jwt>",
  "token_type": "Bearer"
}
```

Las solicitudes a endpoints protegidos envían el token en el encabezado:

```http
Authorization: Bearer <token-jwt>
```

La autenticación se implementó mediante una clase personalizada (`presentation/jwt_autenticacion.py`) integrada con DRF. De esta forma, las vistas protegidas utilizan la identidad del usuario autenticado, sin aceptar como prueba de identidad los identificadores proporcionados por el cliente.

### 7.2. Roles y permisos

En `presentation/permisos.py` se definieron permisos basados en los roles del sistema:

| Rol | Operaciones representativas |
|---|---|
| Administrador | Gestión de organizaciones, categorías y usuarios. |
| Representante donante | Publicación de donaciones y aceptación de solicitudes. |
| Representante beneficiaria | Creación y cancelación de solicitudes. |
| Representantes de organizaciones | Coordinación de entregas, según las reglas aplicables. |

Los permisos de las vistas se complementan con verificaciones de negocio sobre la propiedad y la relación de los usuarios con los recursos. Por tanto, contar con un rol habilitado no significa necesariamente poder modificar cualquier registro del sistema.

### 7.3. Consideraciones de seguridad

La implementación refuerza la separación entre **autenticación** (comprobar quién realiza la petición) y **autorización** (determinar qué operación puede ejecutar). También evita confiar en valores de identidad suministrados en el cuerpo de la solicitud para las operaciones que deben actuar sobre la organización o el usuario autenticado.

Las claves de configuración se obtienen del entorno, y la emisión y validación de tokens se integran con los servicios y componentes de autenticación del proyecto.

## 8. Documentación OpenAPI y Swagger UI

Se integró **drf-spectacular** para generar el esquema OpenAPI de la API y visualizarlo mediante Swagger UI. Las rutas de documentación se registraron en `config/urls.py`:

| Ruta | Propósito |
|---|---|
| `/api/schema/` | Obtener el esquema OpenAPI generado por la aplicación. |
| `/api/docs/` | Explorar los endpoints mediante Swagger UI. |

Las vistas utilizan decoradores `@extend_schema` para definir identificadores de operación, resúmenes, descripciones, parámetros, serializers de entrada y tipos de respuesta. También se documentó la estructura real de los listados paginados mediante `respuesta_paginada`.

El archivo `presentation/openapi.py` registra una extensión de autenticación que declara el esquema **HTTP Bearer JWT**. Su carga se realiza desde `presentation/apps.py`, lo cual permite representar adecuadamente en OpenAPI los endpoints protegidos.

Swagger UI funciona como **documentación interactiva del contrato HTTP**; el presente archivo complementa esa referencia con la justificación arquitectónica, las decisiones de implementación y los resultados del laboratorio.

## 9. Pruebas automatizadas e integración continua

### 9.1. Pruebas de la API

Se añadieron o ampliaron pruebas de integración en `main/test/cr/ac/una/alimentaCR/presentation/`, entre ellas:

- `test_organizacion_api.py`, `test_categoria_api.py` y `test_donacion_api.py`.
- `test_usuario_api.py`, `test_solicitud_api.py` y `test_entrega_api.py`.
- `test_auth_api.py` para autenticación y restricciones de acceso.
- `test_exception_handler.py` para el manejo centralizado de errores.
- `test_listados_api.py` para paginación, ordenamiento y filtros.

Estas pruebas comprueban respuestas HTTP, validaciones, reglas de acceso y comportamiento de los endpoints. Se mantienen además pruebas de negocio y persistencia incorporadas en etapas anteriores.

### 9.2. Resultados de ejecución

Durante la validación local de la versión desarrollada para el laboratorio se obtuvo un resultado de **199 pruebas aprobadas**. También se verificó la generación del esquema OpenAPI y la comprobación de configuración de Django mediante `manage.py check`.

La ejecución de GitHub Actions asociada a los cambios fue revisada y se reportó en estado **Success**. Este resultado confirma que el workflow correspondiente terminó correctamente en el entorno de integración continua; no debe confundirse con una medición adicional de cobertura distinta de la que efectúa el propio workflow.

### 9.3. Configuración del CI

El archivo `.github/workflows/ci.yml` define la ejecución automática en eventos `push` y `pull_request`. Utiliza un runner Ubuntu, configura Python 3.9 y un servicio PostgreSQL para pruebas, instala las dependencias del proyecto y ejecuta las siguientes comprobaciones:

```bash
python manage.py check
python -m pytest \
  --cov=cr.ac.una.alimentaCR.business \
  --cov-report=term-missing \
  --cov-fail-under=70 \
  -v
```

El parámetro `--cov-fail-under=70` exige una cobertura mínima del **70 % sobre el paquete de negocio medido**. No representa un porcentaje global de cobertura de todas las capas de la aplicación.

## 10. Resultados y conclusiones

El Laboratorio 5 permitió consolidar una interfaz REST versionada sobre las funcionalidades de AlimentaCR, sin reemplazar la arquitectura ni las reglas de negocio desarrolladas anteriormente. Los recursos principales quedaron accesibles mediante endpoints con responsabilidades definidas y los procesos de publicación, solicitud, cancelación, aceptación y coordinación se integraron con la capa de presentación.

La centralización de errores y el uso de serializers proporcionaron un tratamiento más uniforme de las solicitudes y respuestas. La paginación, el ordenamiento y los filtros facilitaron la consulta controlada de colecciones, mientras que la autenticación JWT y la autorización por roles introdujeron restricciones de acceso acordes con las responsabilidades de los usuarios.

Finalmente, la integración de OpenAPI y Swagger UI hizo posible explorar el contrato de la API, y las pruebas automatizadas junto con GitHub Actions permitieron verificar los cambios tanto localmente como en el flujo de integración continua. En conjunto, estas implementaciones establecieron una base más consistente para el consumo y la evolución posterior de los servicios web de AlimentaCR.

## 11. Referencias internas del proyecto

- `docs/arquitectura/capa-negocio.md`: organización y decisiones de la capa de negocio.
- `docs/persistencia/pruebas-integracion.md`: antecedentes de pruebas de persistencia.
- `docs/adr/`: decisiones arquitectónicas previamente documentadas.
- `main/python/cr/ac/una/alimentaCR/presentation/`: implementación de la API REST.
- `main/python/cr/ac/una/alimentaCR/business/`: servicios y especificaciones de negocio.
- `main/test/cr/ac/una/alimentaCR/presentation/`: pruebas de la API.
- `.github/workflows/ci.yml`: definición de integración continua.

> **Alcance:** este documento describe las implementaciones del Laboratorio 5. Los detalles completos del modelo de datos, las decisiones de persistencia y los patrones de negocio implementados en laboratorios anteriores se conservan en sus respectivos documentos técnicos.
