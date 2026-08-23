# AlimentaCR

Sistema web para la gestión de donaciones de alimentos entre organizaciones donantes y organizaciones beneficiarias.

Proyecto del curso **EIF509 Desarrollo de Aplicaciones Basadas en Web**, Universidad Nacional, II Ciclo 2026.

---

## Equipo

| Kevin Salazar Bravo

| Kimberley Gómez Quesada

---

## Qué es

AlimentaCR es una plataforma web orientada a facilitar la gestión de donaciones de alimentos entre organizaciones donantes y organizaciones beneficiarias en Costa Rica.

El sistema permite administrar el proceso de publicación, solicitud, asignación y entrega de donaciones. Las organizaciones donantes pueden publicar alimentos disponibles y gestionar las solicitudes recibidas, mientras que las organizaciones beneficiarias pueden consultar las donaciones disponibles y solicitar aquellas que necesiten.

El sistema busca centralizar un proceso que actualmente puede depender de llamadas, mensajes o contactos personales, facilitando el seguimiento y aprovechamiento de alimentos aptos para el consumo.

El detalle del dominio, sus entidades, procesos, reglas de negocio y alcance se encuentra en [`docs/Propuesta-Dominio.md`](docs/Propuesta-Dominio.md).

---

## Requisitos

- Python 3.9

- pip

- Git

- Docker Desktop, que incluye Docker Compose

- PostgreSQL 18.6, provisto mediante Docker y sin necesidad de instalación local

- Flyway 13.3.0, provisto mediante Docker y sin necesidad de instalación local

Verifique las versiones instaladas:

```bash
python --version
pip --version
git --version
docker --version
docker compose version
```

---

## 1. Configuración del entorno

### 1.1 Crear el entorno virtual

Desde la raíz del repositorio, cree un entorno virtual de Python:

```bash
python -m venv .venv
```

> Dependiendo de la instalación o del sistema operativo, la instalacion de Python puede estar disponible por medio de la terminal o de instalador en linea:

MAC con Brew: brew install python@3.9

Windows: [https://www.python.org/downloads/release/python-3913/](https://www.python.org/downloads/release/python-3913/)

### 1.2 Activar el entorno virtual

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows - PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows - CMD:**

```cmd
.venv\Scripts\activate.bat
```

Una vez activado correctamente, la terminal debería mostrar `(.venv)` al inicio de la línea.

### 1.3 Instalar las dependencias

Con el entorno virtual activo:

```bash
pip install -r requirements.txt
```

> La configuración de Django se encuentra en `main/python/cr/ac/una/alimentaCR/config`. El archivo `manage.py` configura automáticamente la ruta necesaria para localizar los módulos del proyecto, por lo que no es necesario configurar manualmente `PYTHONPATH`.

> PostgreSQL, Flyway y Docker no se agregan a `requirements.txt`, porque no son dependencias de Python. PostgreSQL y Flyway se obtienen mediante las imágenes definidas en `docker-compose.yml`.

### 1.4 Base de datos

El proyecto utiliza **PostgreSQL** como base de datos relacional. El esquema se administra mediante migraciones versionadas con **Flyway**, y ambos servicios se ejecutan con Docker Compose.

No es necesario instalar PostgreSQL ni Flyway directamente en el sistema operativo. Para ejecutar la capa de datos únicamente se requiere Docker Desktop.

#### 1.4.1 Configurar las variables de entorno

El repositorio incluye el archivo `.env.example` con las variables requeridas.

En macOS o Linux:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

El archivo `.env` debe contener:

```env
POSTGRES_DB=alimentacr
POSTGRES_USER=alimentacr_user
POSTGRES_PASSWORD=cambiar_contrasena
POSTGRES_PORT=5433
```

El archivo `.env` contiene configuración local y no debe agregarse al repositorio.

#### 1.4.2 Validar Docker Compose

Desde la raíz del repositorio, valide la configuración:

```bash
docker compose config
```

Si el comando no presenta errores, la configuración es válida.

#### 1.4.3 Levantar PostgreSQL

Ejecute:

```bash
docker compose up -d postgres
```

La primera ejecución descargará la imagen de PostgreSQL y creará el volumen necesario para conservar los datos.

Compruebe el estado del contenedor:

```bash
docker compose ps
```

El contenedor `alimentacr-postgres` debe aparecer con estado `healthy` antes de ejecutar las migraciones.

#### 1.4.4 Ejecutar las migraciones

Para aplicar todas las migraciones pendientes:

```bash
docker compose run --rm flyway migrate
```

Flyway ejecuta los archivos ubicados en:

```text
database/migrations/
```

Los nombres de las migraciones deben utilizar la siguiente convención:

```text
V<numero>__<descripcion>.sql
```

Por ejemplo:

```text
V1__crear_esquema_relacional.sql
V2__insertar_datos_iniciales.sql
```

La letra `V` debe escribirse en mayúscula y deben utilizarse dos guiones bajos antes de la descripción.

#### 1.4.5 Consultar el estado de las migraciones

```bash
docker compose run --rm flyway info
```

Las migraciones aplicadas correctamente aparecen con estado `Success`. Las migraciones disponibles que todavía no se han ejecutado aparecen con estado `Pending`.

Flyway crea automáticamente la tabla `flyway_schema_history` para registrar las migraciones aplicadas. Esta tabla no debe modificarse manualmente.

#### 1.4.6 Conectarse mediante un cliente gráfico

Opcionalmente, puede utilizarse Postico, pgAdmin, DBeaver u otro cliente compatible con PostgreSQL.

Los datos de conexión son:

```text
Host: localhost
Puerto: 5433
Base de datos: alimentacr
Usuario: alimentacr_user
Contraseña: valor definido en POSTGRES_PASSWORD
```

El puerto externo puede modificarse mediante `POSTGRES_PORT` en `.env`.

Flyway se conecta internamente mediante `postgres:5432`. Este puerto interno no debe reemplazarse por el puerto externo utilizado desde el sistema operativo.

#### 1.4.7 Detener los servicios

Para detener los contenedores sin eliminar los datos:

```bash
docker compose stop
```

Para detener y eliminar los contenedores conservando el volumen de PostgreSQL:

```bash
docker compose down
```

#### 1.4.8 Reconstruir la base de datos

El siguiente comando elimina los contenedores y los volúmenes de la base de datos:

```bash
docker compose down -v
```

> **Advertencia:** este comando elimina todos los datos almacenados en PostgreSQL. Debe utilizarse únicamente cuando se necesite reconstruir la base desde cero.

Después puede reconstruirse ejecutando:

```bash
docker compose up -d postgres
docker compose run --rm flyway migrate
```

---

## 2. Cómo levantar el proyecto

Desde la raíz del repositorio, primero levante PostgreSQL y aplique las migraciones pendientes:

```bash
docker compose up -d postgres
docker compose run --rm flyway migrate
```

Con el entorno virtual activo, verifique que la configuración de Django sea correcta:

```bash
python manage.py check
```

La respuesta esperada es:

```text
System check identified no issues (0 silenced).
```

Luego, inicie el servidor de desarrollo:

```bash
python manage.py runserver 8080
```

La aplicación quedará disponible por defecto en:

```text
http://localhost:8080/api/salud
```

Para detener el servidor utilice `Ctrl + C`.

---

## 3. Cómo verificar que funciona

Cuando se incorpore el endpoint de verificación de salud, también podrá comprobarse el estado de la aplicación mediante:

Abra **dos terminales** desde la raíz del repositorio, con el entorno virtual activo.

**Terminal 1 — iniciar el servidor:**

```bash
python manage.py runserver 8080
```

**Terminal 2 — probar el endpoint de salud:**

```bash
curl http://localhost:8080/api/salud
```

Si la aplicación está corriendo correctamente, este comando debe devolver una respuesta JSON confirmando que el servicio está activo.

## Otros comandos

| Comando | Qué hace |
| --- | --- |
| `python manage.py runserver` | Inicia el servidor de desarrollo |
| `python manage.py check` | Verifica la configuración del proyecto |
| `python manage.py migrate` | Aplica las migraciones pendientes |
| `python manage.py makemigrations` | Genera nuevas migraciones |
| `pytest` | Ejecuta las pruebas automatizadas |
| `pip install -r requirements.txt` | Instala las dependencias del proyecto |
| `docker compose config` | Valida la configuración de Docker Compose |
| `docker compose up -d postgres` | Levanta PostgreSQL en segundo plano |
| `docker compose run --rm flyway migrate` | Aplica las migraciones pendientes de Flyway |
| `docker compose run --rm flyway info` | Muestra el estado de las migraciones de Flyway |
| `docker compose ps` | Muestra el estado de los contenedores |
| `docker compose logs postgres` | Muestra los registros de PostgreSQL |
| `docker compose stop` | Detiene los contenedores sin eliminarlos |
| `docker compose down` | Elimina los contenedores y conserva los volúmenes |
| `docker compose down -v` | Elimina los contenedores y los datos almacenados en los volúmenes |

> El esquema relacional de AlimentaCR se administra mediante Flyway. Los comandos de migración de Django se conservan para los componentes propios del framework cuando correspondan, pero las tablas del dominio se crean mediante los archivos SQL de `database/migrations/`.

---

## Estructura del proyecto

El código de producción se encuentra bajo el paquete `main/python/cr/ac/una/alimentaCR/` y las pruebas bajo `main/test/cr/ac/una/alimentaCR/`.

```text
EIF509-PlataformaDonaciones/

├── database/
│   └── migrations/
│       └── V1__crear_esquema_relacional.sql
│
├── docs/
│   ├── adr/
│   └── Propuesta-Dominio.md
│
├── main/
│   ├── python/
│   │   └── cr/ac/una/alimentaCR/
│   │       ├── presentation/
│   │       ├── business/
│   │       ├── data/
│   │       └── config/
│   │
│   └── test/
│       └── cr/ac/una/alimentaCR/
│
├── .env.example
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Arquitectura por capas

| Capa | Responsabilidad |
| --- | --- |
| `presentation/` | Endpoints REST, serializers y recepción de solicitudes HTTP |
| `business/` | Servicios, reglas de negocio, validaciones y transacciones |
| `data/` | Modelos, repositorios y acceso a datos |
| `config/` | Configuración de Django y de la aplicación |

La dirección de dependencias es estrictamente unidireccional:

```text
presentation -> business -> data
```

La capa de presentación puede utilizar la capa de negocio y la capa de negocio puede utilizar la capa de datos, pero las dependencias nunca deben ocurrir en sentido contrario.

### Reglas de las capas

1. La capa `presentation` no accede directamente a los repositorios.

2. Las reglas y validaciones propias del dominio pertenecen a `business`.

3. La capa `business` no debe depender de componentes HTTP o de presentación.

4. El acceso y persistencia de información corresponde a `data`.

5. Las operaciones transaccionales que involucren reglas de negocio se coordinan desde `business`.

---

## Pruebas

Las pruebas automatizadas se encuentran separadas del código de producción:

```text
main/test/cr/ac/una/alimentaCR/

├── presentation/

├── business/

└── data/
```

La estructura de pruebas refleja las principales capas del sistema, permitiendo probar cada responsabilidad de manera independiente.

Para ejecutar las pruebas:

```bash
pytest
```

---

## Stack tecnológico

| Área | Tecnología |
| --- | --- |
| Lenguaje | Python |
| Framework backend | Django |
| API REST | Django REST Framework |
| Persistencia relacional | Django ORM |
| Base de datos relacional | PostgreSQL |
| Base de datos documental | MongoDB |
| Pruebas | pytest |
| Frontend | React |
| Integración continua | GitHub Actions |

> MongoDB y React serán incorporados cuando correspondan según la evolución y los laboratorios del curso.

---

## Decisiones de arquitectura

Las decisiones arquitectónicas relevantes del proyecto se documentan mediante **Architecture Decision Records (ADR)** en `docs/adr/`.

| ADR | Decisión | Estado |
| --- | --- | --- |
| [ADR-001](docs/adr/ADR-001-seleccion-stack-backend.md) | Python y Django REST Framework como stack backend | Aceptada |

El ADR-001 documenta la decisión de utilizar Python y Django REST Framework como stack alternativo al stack de referencia del curso, así como las alternativas consideradas y sus consecuencias.

---

## Documentación

La documentación del proyecto se encuentra en:

```text
docs/

├── Propuesta-Dominio.md

└── adr/

    └── ADR-001-seleccion-stack-backend.md
```

La propuesta de dominio contiene la descripción del negocio, actores, entidades, relaciones, procesos, reglas y alcance del sistema.

Los ADR registran las decisiones arquitectónicas importantes tomadas durante la evolución del proyecto.

---

## Convenciones

### Ramas

```text
main       versión estable del proyecto

develop    integración de cambios

feature/*  desarrollo de funcionalidades

fix/*      corrección de errores
```

Cada nueva funcionalidad deberá desarrollarse en una rama independiente y posteriormente integrarse mediante un Pull Request.

Ejemplos:

```text
feature/publicar-donacion

feature/solicitar-donacion

feature/gestion-organizaciones

fix/validacion-fecha-donacion
```

### Mensajes de commit

Se utilizarán prefijos para identificar el propósito de cada cambio:

```text
feat:      nueva funcionalidad

fix:       corrección de errores

test:      creación o modificación de pruebas

docs:      cambios de documentación

refactor:  reorganización del código sin cambiar comportamiento

chore:     configuración o mantenimiento
```

Ejemplos:

```text
feat: agregar servicio para publicar donaciones

test: agregar pruebas de validación de solicitudes

docs: documentar alcance del dominio

refactor: separar acceso a datos de lógica de negocio

chore: configurar dependencias iniciales de Django
```

### Idioma y nombres del código

Los conceptos propios del dominio se escribirán en español, evitando tildes, espacios y caracteres especiales en nombres de clases, variables, módulos y archivos.

Los términos técnicos propios del framework o de patrones de desarrollo podrán mantenerse en inglés.

Ejemplos:

```text
donacion

solicitud

organizacion

DonationSerializer

SolicitudService

DonacionRepository
```

Se seguirán las convenciones de nombres de Python, utilizando `snake_case` para módulos, funciones y variables, y `PascalCase` para clases.

---

## Estado del proyecto

El proyecto se encuentra actualmente en su etapa inicial de definición del dominio y configuración de la arquitectura base.

Las funcionalidades serán incorporadas progresivamente durante los laboratorios del curso.
