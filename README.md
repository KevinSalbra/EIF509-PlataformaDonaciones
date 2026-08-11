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

- Python 3
- pip
- Git
- PostgreSQL


Verifique las versiones instaladas:

```bash
python --version
pip --version
git --version
```

---

## 1. Configuración del entorno

### 1.1 Crear el entorno virtual

Desde la raíz del repositorio, cree un entorno virtual de Python:

```bash
python -m venv .venv
```

> Dependiendo de la instalación o del sistema operativo, el comando de Python puede estar disponible como `python3` en lugar de `python`.

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

### 1.4 Base de datos

El proyecto utilizará **PostgreSQL** como base de datos relacional. La configuración definitiva de la conexión y las migraciones correspondientes se incorporarán conforme avance el desarrollo del proyecto.

---

## 2. Cómo levantar el proyecto

Desde la raíz del repositorio y con el entorno virtual activo, primero verifique que la configuración de Django sea correcta:

```bash
python manage.py check
```

La respuesta esperada es:

```text
System check identified no issues (0 silenced).
```

Luego, inicie el servidor de desarrollo:

```bash
python manage.py runserver
```

La aplicación quedará disponible por defecto en:

```text
http://127.0.0.1:8000/
```

Para detener el servidor utilice `Ctrl + C`.

---

## 3. Cómo verificar que funciona

Con el servidor en ejecución, acceda desde el navegador a:

```text
http://127.0.0.1:8000/
```

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

---

## Estructura del proyecto

El código de producción se encuentra bajo el paquete `main/python/cr/ac/una/alimentaCR/` y las pruebas bajo `main/test/cr/ac/una/alimentaCR/`.

```text
EIF509-PlataformaDonaciones/
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