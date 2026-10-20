# Laboratorio 6 — Presentación y despliegue en la nube

**Curso:** EIF509 — Desarrollo de Aplicaciones Basadas en Web  
**Universidad:** Universidad Nacional de Costa Rica  
**Período:** II Ciclo 2026  
**Proyecto:** AlimentaCR  
**Integrantes:** Kevin Salazar Bravo y Kimberley Gómez Quesada

---

## 1. Introducción

El Laboratorio 6 tiene como propósito completar las interfaces de presentación de AlimentaCR y desplegar los componentes del sistema en servicios administrados en la nube. Este trabajo continúa el desarrollo de la API REST realizado en los laboratorios anteriores, incorporando una aplicación de una sola página (SPA) en React, un módulo administrativo basado en MVC y la configuración necesaria para operar el sistema en un entorno de producción.

AlimentaCR es una plataforma destinada a gestionar donaciones de alimentos entre organizaciones donantes y beneficiarias. Su arquitectura combina PostgreSQL para el almacenamiento transaccional y MongoDB para la bitácora de eventos, permitiendo separar la información del dominio de los registros históricos de las operaciones.

Durante este laboratorio se desplegaron el backend, la SPA y las bases de datos utilizando Render y MongoDB Atlas. Asimismo, se configuró la ejecución automática de migraciones mediante Flyway, la autenticación con JWT, las variables de entorno de producción y las conexiones entre los servicios.

El resultado es un sistema accesible mediante direcciones públicas HTTPS, que permite comprobar las funcionalidades principales sin necesidad de instalar el proyecto localmente.

## 2. Objetivos

### 2.1. Objetivo general

Implementar y desplegar las interfaces de presentación de AlimentaCR y sus servicios asociados en una infraestructura administrada en la nube, garantizando la comunicación entre los componentes, la persistencia de los datos y la configuración independiente del entorno de desarrollo.

### 2.2. Objetivos específicos

- Implementar una interfaz SPA en React que consuma los servicios de la API REST y utilice autenticación mediante JWT.
- Incorporar un módulo administrativo MVC con formularios, validaciones, protección CSRF y navegación entre vistas.
- Desplegar el backend y la SPA en Render, utilizando servicios independientes.
- Configurar PostgreSQL administrado y MongoDB Atlas para la persistencia de información.
- Automatizar la aplicación de migraciones relacionales mediante Flyway durante el arranque del backend.
- Administrar la configuración de producción mediante variables de entorno y comprobar el funcionamiento de los servicios desplegados.

---

## 3. Arquitectura de despliegue

### 3.1. Descripción general

AlimentaCR utiliza una arquitectura en la que las interfaces de presentación se comunican con un backend centralizado, responsable de ejecutar las reglas de negocio y coordinar las operaciones de persistencia.

La SPA React funciona como cliente de la API REST. Por su parte, el módulo administrativo MVC se ejecuta dentro de la aplicación Django y genera las vistas HTML desde el servidor.

Ambas interfaces reutilizan la lógica del dominio implementada en la capa de negocio.

La persistencia se distribuye entre PostgreSQL y MongoDB de acuerdo con la naturaleza de los datos:

- **PostgreSQL:** información estructurada y transaccional del dominio.
- **MongoDB:** eventos de la bitácora y registros de acciones relevantes.

### 3.2. Servicios desplegados

| Componente | Plataforma | Función |
|---|---|---|
| SPA React | Render Static Site | Interfaz para usuarios finales. |
| API Django | Render Web Service | API REST y módulo administrativo MVC. |
| PostgreSQL | Render PostgreSQL | Persistencia relacional del dominio. |
| MongoDB | MongoDB Atlas | Persistencia documental de eventos. |
| Flyway | Contenedor del backend | Validación y ejecución de migraciones SQL. |
| Gunicorn | Contenedor del backend | Servidor de aplicación Django en producción. |

### 3.3. Flujo de comunicación

El flujo de una operación iniciada desde React comprende las siguientes etapas:

1. El usuario realiza una acción en la SPA, como consultar o publicar una donación.
2. React envía una solicitud HTTP a la API REST desplegada en Render.
3. Django recibe la solicitud y ejecuta las validaciones correspondientes.
4. La capa de negocio aplica las reglas del dominio y coordina la operación.
5. La capa de datos realiza las operaciones necesarias sobre PostgreSQL.
6. Cuando corresponde registrar un evento, se utiliza MongoDB para almacenar la información de la bitácora.
7. La API devuelve una respuesta HTTP y React presenta el resultado al usuario.

En el módulo MVC, la interacción comienza mediante una solicitud del navegador a una vista Django. El servidor procesa la operación y devuelve una plantilla HTML o una redirección, según corresponda.

### 3.4. Diagrama de despliegue

El diagrama de despliegue representa los servicios utilizados, las conexiones entre ellos y la ubicación de las variables de entorno.

[Consultar diagrama de despliegue](../arquitectura/diagrama-despliegue.md)

Este diagrama complementará la descripción de la infraestructura presentada en esta sección.

---

## 4. Despliegue del backend

### 4.1. Plataforma seleccionada

Para publicar el backend se utilizó Render, mediante un servicio web denominado `alimentacr-api`.

La aplicación Django se ejecuta dentro de un contenedor Docker y utiliza Gunicorn como servidor de producción.

El servicio se encuentra disponible en:

https://alimentacr-api.onrender.com

La documentación Swagger UI puede consultarse en:

https://alimentacr-api.onrender.com/api/docs/

El módulo administrativo MVC se encuentra en:

https://alimentacr-api.onrender.com/panel/

### 4.2. Configuración mediante Docker

El proyecto incorpora un `Dockerfile` en la raíz del repositorio, encargado de preparar el entorno de ejecución del backend.

La imagen utiliza Python 3.11 sobre una distribución ligera de Linux. Durante su construcción se instalan las dependencias del proyecto y se incorporan los componentes necesarios para ejecutar Flyway.

La imagen también contiene el código de Django, las migraciones SQL y el script de inicio de la aplicación.

La configuración permite que el backend se ejecute de forma consistente en el entorno administrado por Render.

### 4.3. Servidor Gunicorn

En producción, Django se ejecuta mediante Gunicorn, en lugar del servidor de desarrollo proporcionado por `manage.py runserver`.

Gunicorn carga la aplicación WSGI y atiende las solicitudes HTTP recibidas por el servicio.

Durante las pruebas de despliegue se verificó en los registros de Render que Gunicorn iniciara correctamente y quedara escuchando en el puerto configurado.

### 4.4. Script de inicio

El backend utiliza el archivo:

`scripts/start.sh`

Este script coordina el arranque de la aplicación y permite ejecutar Flyway antes de iniciar Gunicorn.

La secuencia consiste en:

1. Preparar la conexión con PostgreSQL.
2. Ejecutar la validación y aplicación de migraciones mediante Flyway.
3. Finalizar el proceso de migración.
4. Iniciar Gunicorn para publicar Django.

De esta manera, la actualización del esquema relacional forma parte del proceso de arranque del servicio.

---

## 5. Persistencia y bases de datos

### 5.1. PostgreSQL administrado

Para la persistencia relacional se creó una instancia administrada de PostgreSQL en Render.

La base de datos almacena las entidades principales de AlimentaCR, entre ellas organizaciones, usuarios, categorías, donaciones, solicitudes y entregas.

La conexión se configura mediante variables de entorno, evitando incluir credenciales directamente en el código.

Durante el laboratorio se verificó la disponibilidad de la instancia y la conexión desde el backend.

También se comprobó que las operaciones realizadas desde la SPA persistieran correctamente en PostgreSQL.

### 5.2. MongoDB Atlas

Para la bitácora de eventos se utilizó MongoDB Atlas, mediante un clúster denominado `alimentacr-cluster`.

La base documental utilizada por el sistema es:

`alimentacr_bitacora`

Dentro de ella se encuentra la colección:

`eventos`

Esta colección registra información sobre las acciones relevantes realizadas en la plataforma.

La conexión desde Django se establece mediante `MONGODB_URI`, cuyo valor se administra como una variable de entorno.

### 5.3. Configuración de conectividad

Durante la integración con MongoDB Atlas se presentaron errores relacionados con el establecimiento de conexiones TLS.

Se revisaron las características del entorno local, las bibliotecas de conexión y la configuración de acceso de red del clúster.

Una de las causas identificadas fue la ausencia de direcciones autorizadas en la configuración de acceso de red de MongoDB Atlas.

Después de ajustar los permisos de conectividad, se comprobó el acceso a la base de datos mediante una operación `ping`.

Posteriormente, se verificó la comunicación del sistema desplegado con MongoDB Atlas mediante el registro y la consulta de eventos.

### 5.4. Persistencia políglota

La utilización de PostgreSQL y MongoDB responde a una decisión arquitectónica documentada previamente.

PostgreSQL administra las entidades y relaciones que requieren integridad referencial y consistencia transaccional.

MongoDB permite registrar eventos de manera documental, sin incorporar la bitácora como parte de las tablas transaccionales del dominio.

Esta separación facilita mantener responsabilidades de persistencia diferenciadas.

La justificación detallada se encuentra en el ADR correspondiente:

[ADR-002 — Persistencia políglota](../adr/ADR-002-persistencia-poliglota-postgresql-mongodb.md)

---

## 6. Migraciones automáticas con Flyway

### 6.1. Administración del esquema

El esquema relacional de AlimentaCR se administra mediante Flyway.

Las migraciones se encuentran en:

`database/migrations/`

Los archivos utilizados incluyen:

- `V1__crear_esquema_relacional.sql`
- `V2__insertar_datos_prueba.sql`

La primera migración crea las estructuras relacionales necesarias para el dominio. La segunda incorpora datos iniciales utilizados para las pruebas del sistema.

### 6.2. Integración con el arranque

Flyway se incorporó al proceso de inicio del contenedor de producción.

Antes de ejecutar Gunicorn, el script de arranque utiliza la conexión configurada hacia PostgreSQL y solicita a Flyway que valide y aplique las migraciones pendientes.

Este procedimiento evita depender de una ejecución manual de migraciones después de cada despliegue.

### 6.3. Verificación realizada

Durante las pruebas se confirmó que Flyway reconociera las migraciones disponibles y validara correctamente el esquema.

Los registros del servicio mostraron que las dos migraciones existentes habían sido aplicadas y que la base de datos se encontraba actualizada.

Posteriormente, Gunicorn inició correctamente y el backend quedó disponible para recibir solicitudes.

La ejecución de Flyway también fue probada mediante Docker en el entorno local.

---

## 7. Aplicación SPA en React

### 7.1. Propósito

La SPA constituye la interfaz orientada a los usuarios finales de AlimentaCR.

Está desarrollada con React y utiliza Vite para el entorno de desarrollo y la construcción de producción.

La aplicación se encuentra en la carpeta:

`spa/`

### 7.2. Despliegue en Render

La SPA se publicó como un sitio estático independiente del backend.

**Servicio:** `alimentacr-spa`

**URL pública:**

https://alimentacr-spa.onrender.com

La configuración de construcción utiliza el comando:

`npm install && npm run build`

El directorio publicado corresponde a:

`dist/`

Se configuró una regla de reescritura hacia `index.html` para permitir que las rutas de la aplicación sean atendidas por React.

### 7.3. Comunicación con la API

React utiliza la variable:

`VITE_API_URL`

Esta variable determina la dirección base del backend consumido por la SPA.

En producción, la aplicación se comunica con la API desplegada en Render mediante HTTPS.

El backend dispone de una configuración CORS que autoriza las solicitudes procedentes del dominio público de la SPA.

### 7.4. Autenticación mediante JWT

La autenticación de la API utiliza JSON Web Tokens.

El usuario proporciona sus credenciales mediante la interfaz de inicio de sesión y la aplicación realiza la solicitud correspondiente al backend.

Después de una autenticación exitosa, el cliente puede utilizar el token para acceder a las operaciones protegidas de la API, de acuerdo con los permisos asociados al usuario.

La firma y validación de los tokens se realiza utilizando la configuración de seguridad del backend.

### 7.5. Funcionalidades verificadas

Durante el laboratorio se comprobó el funcionamiento de las siguientes operaciones:

- Inicio de sesión de un usuario representante de una organización donante.
- Consulta del listado de donaciones.
- Publicación de una nueva donación.
- Visualización de la donación publicada.
- Persistencia de la información en PostgreSQL.
- Registro del evento correspondiente en MongoDB.

Como prueba funcional, se publicó una donación de frijoles negros desde la SPA.

Posteriormente, se comprobó la existencia del registro en PostgreSQL y del evento `DONACION_PUBLICADA` en MongoDB.

Esta verificación permitió confirmar la comunicación entre la interfaz, el backend y las dos bases de datos.

---

## 8. Módulo administrativo MVC

### 8.1. Descripción

El módulo administrativo permite gestionar información del dominio mediante vistas HTML generadas en el servidor.

Se implementó utilizando Django y su sistema de plantillas, aprovechando la arquitectura y los servicios existentes del proyecto.

A diferencia de la SPA, este módulo no requiere una aplicación React independiente para renderizar sus páginas.

El panel se encuentra disponible en:

https://alimentacr-api.onrender.com/panel/

### 8.2. Funcionalidades implementadas

Entre las operaciones verificadas se encuentran:

- Autenticación para acceder al panel.
- Consulta de categorías.
- Creación y edición de categorías.
- Consulta de organizaciones.
- Edición de organizaciones.
- Validación de campos obligatorios.
- Paginación de listados administrativos.

Estas operaciones permiten realizar tareas de administración mediante formularios y vistas del lado del servidor.

### 8.3. Validación de formularios

Los formularios administrativos aplican validaciones antes de guardar los cambios.

Se comprobó el comportamiento de los campos obligatorios y la presentación de errores cuando se omite información requerida.

De esta manera, las operaciones no dependen exclusivamente de validaciones del navegador.

### 8.4. Patrón Post/Redirect/Get

El módulo utiliza el patrón Post/Redirect/Get para evitar que el navegador repita una operación de escritura al actualizar la página después de guardar información.

Durante las pruebas se creó una categoría y se actualizó posteriormente la página.

Se comprobó que la actualización no provocara una nueva solicitud de envío del formulario.

### 8.5. Protección CSRF

Los formularios del panel utilizan la protección CSRF proporcionada por Django.

Las plantillas incorporan el token correspondiente mediante:

`{% csrf_token %}`

Esto permite que Django valide las solicitudes que modifican información mediante formularios.

### 8.6. Paginación

Los listados administrativos utilizan la funcionalidad `Paginator` de Django, con un tamaño de página configurado para los resultados.

Se comprobó el comportamiento de los parámetros de página inválidos o fuera de rango.

Debido a la cantidad limitada de registros disponibles durante las pruebas, no se realizó una demostración de navegación entre varias páginas con conjuntos de datos extensos.

### 8.7. Consideración sobre el framework

El módulo MVC de AlimentaCR utiliza Django Templates, en coherencia con el stack tecnológico adoptado en el proyecto.

La guía del Laboratorio 6 presenta Spring MVC y Thymeleaf como tecnologías de referencia para este componente.

Por esta razón, se realizó una consulta al profesor sobre la aceptación de la implementación equivalente mediante Django MVC. La confirmación de esta equivalencia se encuentra pendiente.

---

## 9. Configuración de entornos y seguridad

### 9.1. Separación de configuración

La aplicación utiliza variables de entorno para diferenciar las configuraciones locales de las utilizadas en producción.

El backend mantiene su configuración principal en:

`main/python/cr/ac/una/alimentaCR/config/settings.py`

Las opciones se determinan a partir de las variables disponibles en cada entorno.

En desarrollo se utilizan principalmente los servicios definidos mediante Docker Compose.

En producción, las conexiones se dirigen a los servicios administrados de Render y MongoDB Atlas.

### 9.2. Variables de entorno

Las principales variables utilizadas por el proyecto son:

| Variable | Propósito |
|---|---|
| `SECRET_KEY` | Clave utilizada por Django y para la firma de JWT. |
| `DEBUG` | Configuración del modo de depuración. |
| `ALLOWED_HOSTS` | Hosts autorizados por Django. |
| `POSTGRES_DB` | Nombre de la base de datos relacional. |
| `POSTGRES_USER` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL. |
| `POSTGRES_HOST` | Servidor PostgreSQL. |
| `POSTGRES_PORT` | Puerto de conexión a PostgreSQL. |
| `MONGODB_URI` | Cadena de conexión a MongoDB. |
| `MONGO_DATABASE` | Base de datos documental utilizada. |
| `CORS_ALLOWED_ORIGINS` | Orígenes autorizados para consumir la API. |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables para la protección CSRF. |
| `VITE_API_URL` | Dirección de la API utilizada por React. |

Los valores sensibles no se incluyen en este documento ni en el README.

### 9.3. Gestión de secretos

Las credenciales y claves utilizadas en producción se configuran mediante las variables de entorno de los servicios.

El archivo `.env` se utiliza para la configuración local y no debe versionarse.

También se comprobó la utilización de una clave de producción diferente de la empleada en el entorno local.

Durante el laboratorio se realizó una prueba de cambio de la clave de producción y se verificó posteriormente que la autenticación de React continuara funcionando.

### 9.4. CORS

Debido a que React y Django se encuentran publicados en servicios independientes, utilizan orígenes diferentes.

Para permitir la comunicación entre ambos se configuró `CORS_ALLOWED_ORIGINS` con el dominio autorizado de la SPA.

Esta configuración permite que el navegador realice las solicitudes correspondientes a la API sin habilitar indiscriminadamente cualquier origen.

### 9.5. CSRF y sesiones

El panel administrativo utiliza sesiones de Django y protección CSRF en los formularios.

La configuración contempla cookies seguras en producción, atributos `HttpOnly` y una política `SameSite`.

También se utiliza la configuración del proxy HTTPS para interpretar correctamente las solicitudes recibidas a través de Render.

### 9.6. HTTPS

Los servicios públicos de Render utilizan direcciones HTTPS.

Esto permite que la comunicación entre el navegador, la SPA y el backend se realice mediante conexiones cifradas.

Las conexiones de las bases de datos se administran mediante los mecanismos de conexión proporcionados por sus respectivas plataformas.

---

## 10. Pruebas funcionales del despliegue

### 10.1. Propósito de las pruebas

Las pruebas realizadas buscaron comprobar que los componentes desplegados funcionaran de forma integrada y que las operaciones principales se completaran correctamente.

Se verificó tanto el acceso a los servicios como la persistencia de información y el registro de eventos.

### 10.2. Resultados

| Componente | Prueba realizada | Resultado |
|---|---|---|
| Backend | Inicio de Django mediante Gunicorn en Render. | Correcto |
| API REST | Acceso al servicio desplegado. | Correcto |
| Swagger UI | Acceso a la documentación de la API. | Correcto |
| PostgreSQL | Conexión con la base de datos administrada. | Correcto |
| Flyway | Validación y aplicación de migraciones en el arranque. | Correcto |
| MongoDB Atlas | Conexión y consulta de eventos. | Correcto |
| React | Inicio de sesión mediante JWT. | Correcto |
| React | Consulta de donaciones. | Correcto |
| React | Publicación de una donación. | Correcto |
| Persistencia | Verificación de la donación publicada en PostgreSQL. | Correcto |
| Bitácora | Verificación del evento en MongoDB. | Correcto |
| Panel MVC | Acceso mediante autenticación. | Correcto |
| Panel MVC | Creación y edición de categorías. | Correcto |
| Panel MVC | Edición de organizaciones. | Correcto |
| Panel MVC | Validación de formularios. | Correcto |
| Panel MVC | Patrón Post/Redirect/Get. | Correcto |
| Panel MVC | Manejo de parámetros de paginación inválidos. | Correcto |
| Seguridad | Cambio de clave de producción y nueva autenticación. | Correcto |

Los resultados corresponden a las verificaciones realizadas durante el desarrollo del laboratorio y no sustituyen las pruebas automatizadas del proyecto.

### 10.3. Verificación de persistencia

La publicación de una donación desde React permitió comprobar el recorrido de una operación a través de los componentes del sistema.

El registro de la donación se verificó mediante un cliente PostgreSQL y el evento de publicación mediante MongoDB Compass.

Esto confirmó que la operación alcanzó las dos tecnologías de persistencia utilizadas por AlimentaCR.

---

## 11. Dificultades y soluciones

### 11.1. Conectividad con MongoDB Atlas

Durante la configuración de MongoDB Atlas se presentaron errores TLS y tiempos de espera de conexión.

Se revisó la configuración del cliente, las características del entorno de ejecución y las direcciones autorizadas en Network Access.

Después de ajustar la configuración de acceso, se comprobó la conectividad y posteriormente el registro de eventos desde el sistema desplegado.

### 11.2. Migraciones en producción

Inicialmente, la ejecución de migraciones sobre PostgreSQL administrado requería una operación independiente.

Para automatizar este proceso, se incorporó Flyway al contenedor del backend y se creó un script de inicio encargado de ejecutar las migraciones antes de Gunicorn.

La solución fue comprobada mediante los registros del despliegue.

### 11.3. Comunicación entre React y Django

Al publicar React y Django en dominios diferentes fue necesario configurar la dirección pública de la API y los orígenes autorizados.

Se utilizó `VITE_API_URL` en la SPA y `CORS_ALLOWED_ORIGINS` en el backend.

Posteriormente, se verificó el inicio de sesión y la publicación de donaciones desde la interfaz desplegada.

### 11.4. Configuración de seguridad

El despliegue requirió adaptar opciones de Django que difieren entre desarrollo y producción.

Se configuraron los hosts autorizados, los orígenes confiables, las cookies y la clave utilizada por la aplicación.

También se verificó el comportamiento de la autenticación después de modificar la clave de producción.

---

## 12. Limitaciones y consideraciones

El despliegue realizado permite comprobar la integración de los componentes principales, pero presenta algunas consideraciones.

**Servicios gratuitos.** Los servicios de Render pueden suspenderse temporalmente después de períodos de inactividad, provocando una demora en la primera solicitud mientras se reactivan.

**Volumen de datos de prueba.** Los registros disponibles permiten comprobar los listados y operaciones principales, pero no constituyen una carga de datos extensa para evaluar rendimiento o navegación entre numerosas páginas.

**Módulo MVC.** La implementación utiliza Django Templates en lugar de Thymeleaf. La aceptación de esta alternativa depende de la confirmación del profesor.

**Configuración por entornos.** La separación entre desarrollo y producción se realiza mediante variables de entorno en una configuración Django compartida. No se implementaron archivos de configuración independientes para cada perfil.

**Alcance de las pruebas.** Las verificaciones funcionales realizadas no representan una evaluación exhaustiva de rendimiento, concurrencia o seguridad.

Estas consideraciones permiten delimitar el alcance del trabajo presentado y diferenciar las funcionalidades comprobadas de posibles mejoras futuras.

---

## 13. Conclusiones

El Laboratorio 6 permitió avanzar de una API REST desarrollada y probada localmente hacia una aplicación web integrada y accesible desde servicios administrados en la nube.

La incorporación de React proporcionó una interfaz orientada al usuario final, mientras que el módulo administrativo MVC permitió gestionar información del dominio mediante vistas renderizadas en el servidor.

El despliegue de PostgreSQL y MongoDB Atlas mantuvo la separación de responsabilidades de persistencia definida en los laboratorios anteriores. Las pruebas de publicación de donaciones permitieron comprobar la comunicación entre React, Django y ambas bases de datos.

La integración de Flyway al proceso de arranque representó una mejora importante en la administración del esquema relacional, al automatizar la validación y aplicación de migraciones antes de iniciar el servicio.

Finalmente, el uso de variables de entorno permitió adaptar la aplicación al entorno de producción sin incorporar directamente las credenciales al código fuente.

En conjunto, el laboratorio consolidó la arquitectura de AlimentaCR y permitió comprobar el funcionamiento integrado de sus componentes principales en la nube.

---

## 14. Referencias internas

- [README del proyecto](../../README.md)
- [Propuesta de dominio](../Propuesta-Dominio.md)
- [Documentación de API REST](../api-rest/)
- [Decisiones arquitectónicas](../adr/)
- [Modelo de datos](../modelo-datos/)
- [Arquitectura](../arquitectura/)

### Enlaces del sistema

| Recurso | Dirección |
|---|---|
| SPA React | https://alimentacr-spa.onrender.com |
| API Django | https://alimentacr-api.onrender.com |
| Swagger UI | https://alimentacr-api.onrender.com/api/docs/ |
| Panel administrativo | https://alimentacr-api.onrender.com/panel/ |

---

**Universidad Nacional de Costa Rica — EIF509 Desarrollo de Aplicaciones Basadas en Web — Laboratorio 6 — II Ciclo 2026.**