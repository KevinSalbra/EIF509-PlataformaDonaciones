# Pruebas de integración

## 1. Propósito

Las pruebas de integración de AlimentaCR verifican que la capa de persistencia funcione correctamente al interactuar con una instancia real de PostgreSQL.

A diferencia de una prueba unitaria, estas pruebas no sustituyen la base de datos mediante mocks. Durante la ejecución se levanta una instancia temporal de PostgreSQL utilizando Testcontainers, se prepara el esquema mediante Flyway y posteriormente se ejecutan las consultas del ORM y de los repositorios de la aplicación.

Este enfoque permite comprobar de forma conjunta el funcionamiento de:

- Django ORM.
- Repositorios de acceso a datos.
- PostgreSQL.
- Migraciones de Flyway.
- Datos de prueba.
- Consultas de negocio.
- Configuración de persistencia utilizada por la aplicación.

---

## 2. Tecnologías utilizadas

La estrategia de pruebas de integración utiliza las siguientes herramientas:

| Tecnología | Uso |
|---|---|
| Python 3.9 | Lenguaje utilizado por el proyecto |
| Django 4.2.30 | Framework y ORM |
| pytest | Ejecución de las pruebas |
| pytest-django | Integración entre pytest y Django |
| Testcontainers | Creación de una instancia temporal de PostgreSQL |
| PostgreSQL 18.6 | Base de datos relacional utilizada durante las pruebas |
| Flyway 13.3.0 | Creación y preparación del esquema de pruebas |
| Docker | Ejecución de PostgreSQL y Flyway |

La versión de Testcontainers utilizada en el proyecto es compatible con Python 3.9.

---

## 3. Estrategia de ejecución

La preparación del entorno de integración se encuentra centralizada en:

```text
main/test/cr/ac/una/alimentaCR/conftest.py
```

El flujo general de ejecución es el siguiente:

```text
pytest
  |
  v
conftest.py
  |
  v
Testcontainers
  |
  v
PostgreSQL 18.6 temporal
  |
  v
pytest-django prepara la base de pruebas
  |
  v
Flyway ejecuta las migraciones
  |
  v
V1: creación del esquema
V2: inserción de datos de prueba
  |
  v
Django ORM
  |
  v
Repositories
  |
  v
Pruebas de integración
  |
  v
El contenedor temporal es eliminado
```

De esta manera, cada ejecución parte de un entorno controlado y reproducible.

No es necesario levantar manualmente PostgreSQL mediante `docker compose up` para ejecutar estas pruebas. Únicamente se requiere que Docker se encuentre disponible, ya que Testcontainers administra automáticamente el ciclo de vida del contenedor temporal.

---

## 4. Preparación del esquema con Flyway

Los modelos Django asociados a las tablas relacionales utilizan el esquema definido por las migraciones del proyecto. Por esta razón, las pruebas no dependen de que Django genere las tablas del dominio.

Durante la preparación de la base temporal, Flyway aplica las migraciones ubicadas en:

```text
database/migrations/
```

La migración V1 crea la estructura relacional y la migración V2 incorpora los datos de prueba utilizados por las consultas de integración.

Esto permite que el entorno de pruebas utilice el mismo esquema versionado que el resto del proyecto y evita mantener una definición paralela de la base de datos únicamente para las pruebas.

---

## 5. Pruebas de repositorios

Se implementaron seis pruebas de integración dirigidas específicamente a comprobar la capa de repositorios.

### 5.1 Donaciones disponibles

Se verifica el método:

```python
DonacionRepository.obtener_disponibles()
```

La prueba comprueba que el repositorio retorne registros y que todas las donaciones obtenidas tengan estado `DISPONIBLE`.

---

### 5.2 Donaciones disponibles por categoría

Se verifica el método:

```python
DonacionRepository.obtener_disponibles_por_categoria(categoria_id)
```

La prueba utiliza una categoría existente en los datos cargados mediante Flyway y comprueba simultáneamente que:

- las donaciones estén disponibles;
- pertenezcan a la categoría solicitada.

Esta prueba cubre una de las consultas directas de negocio desarrolladas para la capa de persistencia.

---

### 5.3 Filtro dinámico de donaciones

Se verifica:

```python
DonacionRepository.filtrar_donaciones(...)
```

La prueba combina los filtros de estado y organización donante.

Se comprueba que cada registro retornado cumpla ambas condiciones, validando el funcionamiento de la consulta dinámica implementada mediante la construcción progresiva de un `QuerySet`.

---

### 5.4 Solicitudes pendientes por donación

Se verifica:

```python
SolicitudRepository.obtener_pendientes_por_donacion(donacion_id)
```

La prueba comprueba que todas las solicitudes obtenidas:

- tengan estado `PENDIENTE`;
- correspondan a la donación indicada.

Esta prueba cubre la segunda consulta directa de negocio implementada en los repositorios.

---

### 5.5 Filtro dinámico de solicitudes

Se verifica:

```python
SolicitudRepository.filtrar_solicitudes(...)
```

La prueba combina los filtros de estado y donación.

Cada resultado debe cumplir las condiciones especificadas, comprobando que la consulta dinámica de solicitudes se construya correctamente.

---

### 5.6 Método heredado del repositorio base

Se verifica el uso de:

```python
DonacionRepository.obtener_por_id(id)
```

El método `obtener_por_id` se encuentra definido en `BaseRepository` y es heredado por `DonacionRepository`.

La prueba confirma que la generalización de repositorios funciona correctamente y que una implementación específica puede utilizar las operaciones comunes definidas en la clase base.

El flujo correspondiente es:

```text
DonacionRepository
        |
        | hereda
        v
BaseRepository.obtener_por_id()
        |
        v
Donacion.objects.filter(...)
        |
        v
PostgreSQL
```

---

## 6. Pruebas adicionales de persistencia

Además de las seis pruebas de integración de repositorios, la suite contiene pruebas adicionales relacionadas con la capa de persistencia.

### 6.1 Evidencia del problema N+1

Se mantiene una prueba que obtiene donaciones y posteriormente accede a sus relaciones `organizacion_donante` y `categoria` sin una optimización previa.

Durante la ejecución observada se generaron:

```text
13 consultas SQL
```

El comportamiento corresponde al problema N+1, ya que se realiza una consulta inicial para las donaciones y posteriormente consultas adicionales al acceder a las relaciones de cada entidad.

### 6.2 Corrección del problema N+1

La consulta se optimiza mediante:

```python
select_related(
    "organizacion_donante",
    "categoria"
)
```

Con esta estrategia Django obtiene las relaciones requeridas mediante `JOIN`, reduciendo el resultado observado a:

```text
1 consulta SQL
```

Por lo tanto, la evidencia obtenida es:

| Escenario | Consultas |
|---|---:|
| Sin optimización | 13 |
| Con `select_related()` | 1 |

### 6.3 Prueba de infraestructura

También se conserva una prueba destinada a verificar que la infraestructura temporal de PostgreSQL se encuentre disponible durante la ejecución.

---

## 7. Resultado de la suite

Una vez integradas las pruebas de repositorios, las pruebas de N+1 y la comprobación de infraestructura, la suite completa presenta el siguiente resultado:

```text
9 passed
```

La distribución de pruebas es:

```text
9 pruebas
|
+-- 6 pruebas de integración de repositorios
|
+-- 2 pruebas relacionadas con N+1
|
+-- 1 prueba de infraestructura
```

Todas se ejecutan utilizando el PostgreSQL temporal administrado mediante Testcontainers.

---

## 8. Ejecución local

### Requisitos

Antes de ejecutar la suite se requiere:

- Python 3.9 con el entorno virtual activo.
- Dependencias de `requirements.txt` instaladas.
- Docker Desktop o un motor Docker compatible en ejecución.

Las dependencias pueden instalarse mediante:

```bash
pip install -r requirements.txt
```

No es necesario iniciar previamente los servicios del proyecto mediante Docker Compose.

### Ejecutar toda la suite

Desde la raíz del repositorio:

```bash
python -m pytest -v -s
```

### Ejecutar únicamente las pruebas de integración de donaciones

```bash
python -m pytest \
main/test/cr/ac/una/alimentaCR/data/test_donacion_repository_integracion.py \
-v -s
```

### Ejecutar únicamente las pruebas de integración de solicitudes

```bash
python -m pytest \
main/test/cr/ac/una/alimentaCR/data/test_solicitud_repository_integracion.py \
-v -s
```

---

## 9. Integración continua

La misma suite de pruebas forma parte del proceso de integración continua del repositorio.

Esto permite comprobar que los cambios incorporados al proyecto continúen siendo compatibles con:

- la configuración de Django;
- el esquema administrado mediante Flyway;
- PostgreSQL;
- los repositorios;
- las consultas de negocio;
- las optimizaciones de acceso a datos.

De esta forma, el resultado de las pruebas no depende únicamente del entorno local de desarrollo.

---

## 10. Conclusión

La incorporación de Testcontainers permite que las pruebas de integración de AlimentaCR se ejecuten contra una instancia real y temporal de PostgreSQL, manteniendo aislamiento entre ejecuciones y evitando la dependencia de una base de datos compartida.

La preparación del esquema mediante Flyway garantiza además que las pruebas utilicen las mismas migraciones versionadas que definen la estructura relacional del proyecto.

Con las seis pruebas específicas de repositorios, las pruebas de N+1 y la validación de infraestructura, la suite proporciona evidencia del funcionamiento de la capa de persistencia, de la generalización de repositorios y de las consultas de negocio implementadas durante el Laboratorio 3.

