# AlimentaCR

Sistema web para la gestión de donaciones de alimentos entre organizaciones donantes y organizaciones beneficiarias.

Proyecto del curso **EIF509 - Desarrollo de Aplicaciones Basadas en Web**, Universidad Nacional de Costa Rica, II Ciclo 2026.

---

## Equipo de desarrollo

- Kevin Salazar Bravo
- Kimberley Gómez Quesada

## 1. Descripción del proyecto

AlimentaCR es una plataforma web orientada a facilitar la gestión de donaciones de alimentos entre organizaciones donantes y beneficiarias en Costa Rica.

El sistema permite administrar el proceso de publicación, solicitud, asignación y entrega de donaciones. Las organizaciones donantes pueden publicar alimentos disponibles y gestionar las solicitudes recibidas, mientras que las organizaciones beneficiarias pueden consultar las donaciones disponibles y solicitar aquellos alimentos que necesiten.

La plataforma busca centralizar un proceso que actualmente puede depender de llamadas, mensajes o contactos personales, facilitando el seguimiento de las donaciones y el aprovechamiento de alimentos aptos para el consumo.

El detalle del dominio, sus entidades, procesos, reglas de negocio y alcance se encuentra en [docs/Propuesta-Dominio.md](docs/Propuesta-Dominio.md).

---

## 2. Sistema desplegado

AlimentaCR se encuentra desplegado en servicios administrados en la nube, utilizando Render para la aplicación y MongoDB Atlas para la base de datos documental.

### Enlaces públicos

| Componente | Enlace |
|---|---|
| Aplicación web React (SPA) | [Abrir AlimentaCR](https://alimentacr-spa.onrender.com) |
| API REST | [API AlimentaCR](https://alimentacr-api.onrender.com) |
| Documentación Swagger UI | [Consultar Swagger](https://alimentacr-api.onrender.com/api/docs/) |
| Esquema OpenAPI | [Consultar esquema](https://alimentacr-api.onrender.com/api/schema/) |
| Panel administrativo MVC | [Abrir panel administrativo](https://alimentacr-api.onrender.com/panel/) |

Todos los enlaces públicos utilizan HTTPS.

**Nota:** debido a las características de los servicios gratuitos de Render, la primera solicitud puede tardar mientras el servicio se reactiva después de un período de inactividad.

### Acceso para evaluación

El sistema dispone de usuarios de prueba para comprobar las funcionalidades correspondientes a los diferentes roles.

Las credenciales de acceso se proporcionarán al profesor mediante el aula virtual, junto con las direcciones públicas de la aplicación.

Las contraseñas de prueba no se publican en este repositorio.

---

## 3. Arquitectura del sistema

AlimentaCR utiliza una arquitectura por capas en el backend y dispone de dos interfaces de presentación que permiten interactuar con el sistema.

### Componentes principales

| Componente | Responsabilidad |
|---|---|
| SPA React | Interfaz del usuario final; consume la API REST mediante solicitudes HTTP y autenticación JWT. |
| Panel MVC Django | Interfaz administrativa renderizada en el servidor mediante plantillas HTML. |
| API REST | Expone las operaciones del dominio mediante Django REST Framework. |
| Capa de negocio | Implementa servicios, validaciones y reglas de negocio. |
| Capa de datos | Gestiona los modelos, repositorios y operaciones de persistencia. |
| PostgreSQL | Almacena los datos transaccionales y las entidades principales del dominio. |
| MongoDB | Almacena la bitácora de eventos y las acciones relevantes del sistema. |
| Flyway | Administra y aplica las migraciones versionadas de PostgreSQL. |

### Arquitectura por capas

El backend se organiza en los siguientes paquetes:

```text
main/python/cr/ac/una/alimentaCR/
├── presentation/
├── business/
├── data/
└── config/
```

| Capa | Responsabilidad |
|---|---|
| `presentation/` | Endpoints REST, vistas MVC, serializadores y recepción de solicitudes HTTP. |
| `business/` | Servicios, reglas de negocio, validaciones y coordinación de transacciones. |
| `data/` | Modelos, repositorios y acceso a las bases de datos. |
| `config/` | Configuración de Django, rutas y componentes de infraestructura. |

La dirección principal de dependencias es:

```text
presentation → business → data
```

La capa de presentación utiliza los servicios de negocio, mientras que estos coordinan las operaciones de persistencia.

Las reglas propias del dominio se mantienen separadas de los mecanismos de presentación y acceso a datos.

---

## 4. Stack tecnológico

| Área | Tecnología |
|---|---|
| Lenguaje backend | Python |
| Framework backend | Django |
| API REST | Django REST Framework |
| Documentación API | drf-spectacular / Swagger UI |
| Interfaz SPA | React |
| Herramienta de construcción SPA | Vite |
| Interfaz administrativa MVC | Django Templates |
| Autenticación API | JSON Web Tokens (JWT) |
| Persistencia relacional | PostgreSQL |
| Acceso relacional | Django ORM |
| Persistencia documental | MongoDB |
| Migraciones relacionales | Flyway |
| Servidor de producción | Gunicorn |
| Contenedores | Docker y Docker Compose |
| Despliegue de API y SPA | Render |
| Base de datos documental administrada | MongoDB Atlas |
| Pruebas automatizadas | pytest |
| Integración continua | GitHub Actions |

---

## 5. Requisitos para ejecución local

Para ejecutar el proyecto en un entorno de desarrollo se requiere:

- Python 3.9 o una versión compatible con las dependencias del proyecto.
- pip.
- Git.
- Docker Desktop con Docker Compose.
- Node.js y npm para ejecutar la SPA React.

Los servicios de bases de datos se ejecutan mediante Docker, por lo que no es necesario instalar PostgreSQL, MongoDB ni Flyway directamente en el sistema operativo.

El entorno de contenedores utiliza PostgreSQL y MongoDB, mientras que las migraciones relacionales son administradas por Flyway.

### Verificar herramientas

```bash
python --version
pip --version
git --version
docker --version
docker compose version
node --version
npm --version
```

---

## 6. Configuración del entorno local

### 6.1. Clonar el repositorio

```bash
git clone https://github.com/KevinSalbra/EIF509-PlataformaDonaciones.git

cd EIF509-PlataformaDonaciones
```

### 6.2. Crear el entorno virtual

Desde la raíz del repositorio:

```bash
python -m venv .venv
```

Activar el entorno virtual:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows CMD**

```cmd
.venv\Scripts\activate.bat
```

Una vez activado, la terminal mostrará normalmente `(.venv)` al inicio de la línea.

### 6.3. Instalar dependencias de Python

```bash
python -m pip install -r requirements.txt
```

La configuración de Django se encuentra en:

```text
main/python/cr/ac/una/alimentaCR/config/
```

El archivo `manage.py`, ubicado en la raíz, configura la ruta necesaria para localizar los módulos del proyecto.

### 6.4. Configurar las variables de entorno

El proyecto utiliza variables de entorno para mantener la configuración y las credenciales separadas del código fuente.

Si existe el archivo `.env.example`, puede utilizarse como plantilla.

**macOS / Linux**

```bash
cp .env.example .env
```

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

El archivo `.env` debe configurarse con los valores correspondientes al entorno local.

#### Variables del backend

| Variable | Propósito |
|---|---|
| `SECRET_KEY` | Clave de firma utilizada por Django y los JWT del proyecto. |
| `DEBUG` | Activa o desactiva el modo de depuración. |
| `ALLOWED_HOSTS` | Define los hosts autorizados para acceder a Django. |
| `POSTGRES_DB` | Nombre de la base de datos PostgreSQL. |
| `POSTGRES_USER` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL. |
| `POSTGRES_HOST` | Dirección del servidor PostgreSQL. |
| `POSTGRES_PORT` | Puerto de conexión a PostgreSQL. |
| `MONGODB_URI` | Cadena de conexión utilizada para acceder a MongoDB. |
| `MONGO_DATABASE` | Nombre de la base de datos documental. |
| `MONGO_ROOT_USERNAME` | Usuario administrador de MongoDB local. |
| `MONGO_ROOT_PASSWORD` | Contraseña del administrador de MongoDB local. |
| `MONGO_PORT` | Puerto utilizado por MongoDB local. |
| `CORS_ALLOWED_ORIGINS` | Orígenes autorizados para consumir la API desde el navegador. |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables para las operaciones protegidas mediante CSRF. |

Las variables `MONGO_ROOT_USERNAME`, `MONGO_ROOT_PASSWORD` y `MONGO_PORT` corresponden a la configuración de los contenedores locales.

#### Variables de despliegue

| Variable | Propósito |
|---|---|
| `PORT` | Puerto asignado al servicio web por la plataforma de despliegue. |
| `VITE_API_URL` | URL pública de la API utilizada durante la construcción de React. |

**Importante:** los valores de contraseñas, claves y cadenas de conexión privadas no deben incluirse en el repositorio.

El archivo `.env` debe permanecer excluido mediante `.gitignore`.

---

## 7. Bases de datos locales

### 7.1. PostgreSQL

PostgreSQL almacena la información transaccional del sistema, incluyendo las entidades principales del dominio.

El esquema relacional se administra mediante migraciones SQL versionadas con Flyway.

Para levantar PostgreSQL:

```bash
docker compose up -d postgres
```

Para comprobar el estado del contenedor:

```bash
docker compose ps
```

### 7.2. Aplicar migraciones con Flyway

Ejecute:

```bash
docker compose run --rm flyway migrate
```

Las migraciones se encuentran en:

```text
database/migrations/
```

Los archivos siguen la convención:

```text
V<numero>__<descripcion>.sql
```

Por ejemplo:

```text
V1__crear_esquema_relacional.sql
V2__insertar_datos_prueba.sql
```

La letra `V` debe escribirse en mayúscula y deben utilizarse dos guiones bajos antes de la descripción.

Para consultar el estado de las migraciones:

```bash
docker compose run --rm flyway info
```

Flyway registra las migraciones aplicadas en la tabla `flyway_schema_history`.

### 7.3. MongoDB

MongoDB almacena la bitácora de eventos del sistema, siguiendo un enfoque de persistencia políglota.

PostgreSQL conserva el estado actual de las entidades, mientras que MongoDB registra los eventos asociados a las operaciones relevantes.

Para levantar MongoDB:

```bash
docker compose up -d mongodb
```

La inicialización local utiliza los scripts ubicados en:

```text
database/mongodb/init/
```

Estos scripts permiten preparar la colección de eventos, sus índices y los datos de inicialización.

Para verificar el estado del servicio:

```bash
docker compose ps
```

La justificación de este diseño se encuentra en [docs/modelo-datos/modelo-mongodb.md](docs/modelo-datos/modelo-mongodb.md).

### 7.4. Levantar ambas bases de datos

Desde la raíz del proyecto:

```bash
docker compose up -d postgres mongodb
```

Después, aplique las migraciones:

```bash
docker compose run --rm flyway migrate
```

### 7.5. Detener los servicios

Para detener los contenedores sin eliminar los datos:

```bash
docker compose stop
```

Para eliminar los contenedores conservando los volúmenes:

```bash
docker compose down
```

**Advertencia:** el comando siguiente elimina los volúmenes de datos locales:

```bash
docker compose down -v
```

No debe utilizarse si se necesita conservar la información almacenada en PostgreSQL o MongoDB.

---

## 8. Ejecución del backend

Con las bases de datos disponibles y el entorno virtual activado, verifique la configuración de Django:

```bash
python manage.py check
```

La respuesta esperada, si no existen problemas de configuración, es:

```text
System check identified no issues (0 silenced).
```

Para iniciar el servidor de desarrollo:

```bash
python manage.py runserver 8080
```

El backend estará disponible en:

```text
http://localhost:8080/
```

La documentación Swagger local podrá consultarse en:

```text
http://localhost:8080/api/docs/
```

El panel administrativo MVC estará disponible en:

```text
http://localhost:8080/panel/
```

Para detener el servidor, utilice `Ctrl + C`.

---

## 9. Ejecución de la SPA React

La aplicación React se encuentra en la carpeta:

```text
spa/
```

Desde la raíz del repositorio:

```bash
cd spa
```

Instale las dependencias:

```bash
npm install
```

Configure `VITE_API_URL` con la dirección del backend que utilizará la SPA.

Para iniciar el servidor de desarrollo:

```bash
npm run dev
```

Vite mostrará en la terminal la dirección local donde se encuentra disponible la aplicación.

Para generar la versión de producción:

```bash
npm run build
```

El resultado se genera en la carpeta:

```text
spa/dist/
```

En producción, la SPA se publica como sitio estático en Render.

---

## 10. Interfaces del sistema

### 10.1. API REST

La API está desarrollada con Django REST Framework y expone los servicios del dominio mediante endpoints HTTP.

Las rutas de la API utilizan el prefijo:

```text
/api/v1/
```

La documentación interactiva se encuentra disponible mediante Swagger UI.

**Producción:**

https://alimentacr-api.onrender.com/api/docs/

### 10.2. SPA React

La SPA está orientada al usuario final y consume los servicios expuestos por la API REST.

Entre las funcionalidades implementadas y comprobadas se encuentran:

- Inicio de sesión mediante JWT.
- Consulta de donaciones.
- Publicación de nuevas donaciones.
- Comunicación con la API desplegada en Render.

La interfaz utiliza la configuración `VITE_API_URL` para determinar la dirección del backend.

**Producción:**

https://alimentacr-spa.onrender.com

### 10.3. Panel administrativo MVC

El sistema dispone de un módulo administrativo desarrollado con vistas y plantillas HTML de Django.

Este módulo permite gestionar información administrativa del dominio.

Entre las funcionalidades comprobadas se encuentran:

- Autenticación de usuarios administrativos.
- Consulta de categorías y organizaciones.
- Creación y edición de categorías.
- Edición de organizaciones.
- Validación de formularios.
- Paginación de listados.
- Protección CSRF.
- Patrón Post/Redirect/Get.

**Producción:**

https://alimentacr-api.onrender.com/panel/

El módulo MVC se ejecuta dentro del mismo servicio Django que publica la API REST.

---

## 11. Despliegue en producción

AlimentaCR utiliza servicios administrados en la nube para publicar la aplicación y sus bases de datos.

### 11.1. Servicios utilizados

| Servicio | Plataforma | Función |
|---|---|---|
| `alimentacr-api` | Render Web Service | API REST y panel administrativo Django. |
| `alimentacr-spa` | Render Static Site | Aplicación React. |
| PostgreSQL | Render PostgreSQL | Base de datos relacional. |
| `alimentacr-cluster` | MongoDB Atlas | Base de datos documental y bitácora de eventos. |

### 11.2. Despliegue del backend

El backend utiliza un contenedor Docker que incorpora las dependencias de Python, Django, Gunicorn y Flyway.

El servicio ejecuta el script:

```text
scripts/start.sh
```

Durante el arranque se realizan las siguientes operaciones:

1. Se establece la conexión con PostgreSQL mediante las variables de entorno.
2. Flyway valida y aplica las migraciones pendientes.
3. Si las migraciones finalizan correctamente, se inicia Gunicorn.
4. Gunicorn publica la aplicación Django en el puerto asignado por Render.

Este mecanismo permite mantener actualizado el esquema relacional durante los despliegues.

### 11.3. Despliegue de React

La SPA se publica mediante un servicio de sitios estáticos de Render.

La construcción utiliza:

```bash
npm install && npm run build
```

El directorio publicado es:

```text
dist/
```

La variable `VITE_API_URL` permite configurar la dirección pública de la API durante la construcción.

### 11.4. Configuración de desarrollo y producción

La configuración del backend se administra mediante variables de entorno, sin incorporar credenciales directamente en el código fuente.

El proyecto utiliza un archivo común `settings.py`, cuyo comportamiento cambia según las variables proporcionadas por el entorno.

En desarrollo se utilizan los servicios locales de Docker Compose y las direcciones correspondientes al equipo del desarrollador.

En producción se utilizan los servicios administrados de Render y MongoDB Atlas, con configuraciones independientes para los dominios, conexiones y secretos.

Las claves utilizadas para firmar los JWT de producción se mantienen separadas de las utilizadas en desarrollo.

### 11.5. Seguridad del despliegue

La configuración contempla:

- Uso de HTTPS en los servicios públicos.
- Autenticación mediante JWT para la API.
- Configuración de CORS con el dominio autorizado de React.
- Protección CSRF en los formularios del panel administrativo.
- Cookies seguras cuando `DEBUG=False`.
- Gestión de credenciales y claves mediante variables de entorno.
- Separación de secretos entre desarrollo y producción.

Las contraseñas y claves privadas no se documentan con sus valores reales.

---

## 12. Pruebas y verificación

Las pruebas automatizadas del proyecto se encuentran en:

```text
main/test/cr/ac/una/alimentaCR/
```

Su organización refleja las principales capas del sistema:

```text
main/test/cr/ac/una/alimentaCR/
├── presentation/
├── business/
└── data/
```

Para ejecutar la suite de pruebas:

```bash
pytest
```

### Verificaciones realizadas en producción

Durante el Laboratorio 6 se realizaron pruebas funcionales sobre los servicios desplegados.

| Componente | Verificación |
|---|---|
| API Django | Inicio del servicio y acceso público mediante HTTPS. |
| Swagger UI | Acceso a la documentación interactiva. |
| React | Inicio de sesión, consulta y publicación de donaciones. |
| PostgreSQL | Persistencia de donaciones creadas desde la SPA. |
| MongoDB Atlas | Registro de eventos de publicación en la bitácora. |
| Flyway | Validación y ejecución automática durante el arranque. |
| Panel MVC | Autenticación, formularios, validaciones y navegación administrativa. |
| Configuración | Uso de variables de entorno y dominios autorizados. |

Estas verificaciones complementan las pruebas automatizadas del proyecto.

---

## 13. Estructura del proyecto

La estructura general del repositorio es:

```text
EIF509-PlataformaDonaciones/
│
├── database/
│   ├── migrations/
│   └── mongodb/
│       └── init/
│
├── docs/
│   ├── adr/
│   ├── api-rest/
│   ├── arquitectura/
│   ├── modelo-datos/
│   └── Propuesta-Dominio.md
│
├── main/
│   ├── python/
│   │   └── cr/ac/una/alimentaCR/
│   │       ├── presentation/
│   │       ├── business/
│   │       ├── data/
│   │       └── config/
│   └── test/
│       └── cr/ac/una/alimentaCR/
│
├── scripts/
│   └── start.sh
│
├── spa/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
└── README.md
```

---

## 14. Decisiones de arquitectura

Las decisiones arquitectónicas relevantes se documentan mediante **Architecture Decision Records (ADR)** en `docs/adr/`.

| ADR | Decisión |
|---|---|
| [ADR-001](docs/adr/ADR-001-seleccion-stack-backend.md) | Selección de Python y Django REST Framework como stack backend. |
| [ADR-002](docs/adr/ADR-002-persistencia-poliglota-postgresql-mongodb.md) | Uso de persistencia políglota con PostgreSQL y MongoDB. |

El ADR-001 explica la selección del stack tecnológico, sus alternativas y consecuencias.

El ADR-002 justifica la separación entre la información transaccional del dominio y la bitácora documental de eventos.

---

## 15. Documentación del proyecto

La documentación complementaria se encuentra en la carpeta `docs/`.

| Documento o carpeta | Contenido |
|---|---|
| [Propuesta de dominio](docs/Propuesta-Dominio.md) | Descripción del negocio, actores, entidades, procesos y reglas. |
| [Decisiones de arquitectura](docs/adr/) | ADR de las decisiones técnicas del proyecto. |
| [Arquitectura](docs/arquitectura/) | Diagramas y documentación arquitectónica. |
| [Modelo de datos](docs/modelo-datos/) | Modelos relacional y documental. |
| [API REST](docs/api-rest/) | Documentación de endpoints y funcionalidades REST. |

La documentación específica del Laboratorio 6 incluirá la arquitectura desplegada, configuración de servicios, variables de entorno, funcionamiento de Flyway, pruebas de producción y diagrama de despliegue.

---

## 16. Comandos útiles

| Comando | Descripción |
|---|---|
| `python manage.py runserver 8080` | Inicia el backend local. |
| `python manage.py check` | Verifica la configuración de Django. |
| `python manage.py check --deploy` | Ejecuta comprobaciones adicionales de seguridad. |
| `pytest` | Ejecuta las pruebas automatizadas. |
| `python -m pip install -r requirements.txt` | Instala dependencias de Python. |
| `docker compose config` | Valida la configuración de Docker Compose. |
| `docker compose up -d postgres mongodb` | Inicia las bases de datos locales. |
| `docker compose run --rm flyway migrate` | Aplica migraciones pendientes. |
| `docker compose run --rm flyway info` | Consulta el estado de Flyway. |
| `docker compose ps` | Muestra el estado de los contenedores. |
| `docker compose stop` | Detiene los servicios sin eliminar datos. |
| `docker compose down` | Elimina contenedores conservando los volúmenes. |
| `npm install` | Instala dependencias de React, desde `spa/`. |
| `npm run dev` | Inicia la SPA en desarrollo, desde `spa/`. |
| `npm run build` | Genera la versión de producción de React. |

**Nota sobre migraciones:** Flyway es la fuente de verdad del esquema relacional de AlimentaCR. Los modelos Django correspondientes a las tablas administradas por Flyway se mantienen alineados con las migraciones SQL.

---

## 17. Convenciones de desarrollo

### Ramas

El proyecto utiliza Git para el control de versiones y la colaboración entre integrantes.

Las funcionalidades y correcciones se desarrollan en ramas de trabajo y posteriormente se integran en la rama correspondiente del proyecto.

### Mensajes de commit

Se utilizan prefijos para identificar el propósito de los cambios:

| Prefijo | Propósito |
|---|---|
| `feat:` | Nueva funcionalidad. |
| `fix:` | Corrección de errores. |
| `test:` | Creación o modificación de pruebas. |
| `docs:` | Cambios de documentación. |
| `refactor:` | Reorganización del código sin modificar su comportamiento. |
| `chore:` | Configuración o mantenimiento. |

### Idioma y nombres del código

Los conceptos propios del dominio se expresan principalmente en español, evitando tildes, espacios y caracteres especiales en identificadores.

Se siguen las convenciones habituales de Python:

- `snake_case` para módulos, funciones y variables.
- `PascalCase` para clases.

Los términos técnicos asociados a frameworks, bibliotecas o patrones pueden mantenerse en inglés.

---

## 18. Estado actual del proyecto

AlimentaCR cuenta con una API REST desarrollada en Django, una SPA en React, un módulo administrativo MVC y un entorno de producción desplegado en la nube.

La plataforma utiliza PostgreSQL para los datos transaccionales y MongoDB para la bitácora de eventos. El esquema relacional se administra mediante Flyway, incluyendo la validación y aplicación automática de migraciones durante el arranque del backend en producción.

Las interfaces y servicios principales han sido desplegados y sometidos a verificaciones funcionales.

El proyecto continúa evolucionando mediante los laboratorios del curso EIF509, incorporando mejoras funcionales, pruebas y documentación técnica.

---

**Universidad Nacional de Costa Rica — EIF509 Desarrollo de Aplicaciones Basadas en Web — II Ciclo 2026.**