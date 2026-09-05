# Consultas de negocio y optimización del problema N+1

## 1. Introducción

Como parte de la implementación de la capa de persistencia de AlimentaCR, se desarrollaron consultas orientadas a necesidades específicas del dominio utilizando Django ORM.

Se implementaron cuatro consultas de negocio: dos consultas directas, cuya estructura y criterios están definidos previamente, y dos consultas dinámicas, cuyos filtros se construyen de acuerdo con los parámetros proporcionados.

Adicionalmente, se analizó el problema de consultas N+1 producido por la carga diferida de relaciones entre entidades. Se documentó el comportamiento inicial y posteriormente se aplicó una optimización mediante `select_related()`.

Las pruebas se realizaron utilizando los datos de prueba definidos mediante las migraciones de Flyway.

---

## 2. Consultas directas

### 2.1. Donaciones disponibles por categoría

#### Necesidad de negocio

El sistema requiere consultar las donaciones que se encuentran disponibles y que pertenecen a una categoría determinada. Esta consulta permite limitar los resultados a alimentos que todavía pueden ser solicitados y que pertenecen al tipo de alimento indicado.

#### Implementación

La consulta se implementó en `DonacionRepository` mediante el método:

```python
def obtener_disponibles_por_categoria(self, categoria_id):
    return self.model.objects.filter(
        estado=Donacion.Estado.DISPONIBLE,
        categoria_id=categoria_id
    )
```

Se considera una consulta directa debido a que los criterios que la conforman están definidos previamente: la donación debe encontrarse en estado `DISPONIBLE` y debe pertenecer a la categoría indicada.

#### Prueba realizada

Se ejecutó la consulta utilizando la categoría con identificador `4`:

```python
donaciones = repositorio.obtener_disponibles_por_categoria(4)
```

El resultado obtenido fue:

```text
<QuerySet [<Donacion: Leche de larga duración - 30.00 LITRO>]>

6 Leche de larga duración DISPONIBLE 4 2
```

Por lo tanto, la consulta encontró una donación disponible perteneciente a la categoría seleccionada.

#### SQL generado

Django ORM generó la siguiente consulta:

```sql
SELECT
    "donacion"."id_donacion",
    "donacion"."id_organizacion_donante",
    "donacion"."id_categoria",
    "donacion"."alimento",
    "donacion"."descripcion",
    "donacion"."cantidad",
    "donacion"."unidad_medida",
    "donacion"."fecha_publicacion",
    "donacion"."fecha_limite_retiro",
    "donacion"."estado"
FROM "donacion"
WHERE (
    "donacion"."id_categoria" = 4
    AND "donacion"."estado" = DISPONIBLE
);
```

---

### 2.2. Solicitudes pendientes por donación

#### Necesidad de negocio

El sistema requiere consultar las solicitudes pendientes asociadas a una donación específica. Esta información puede utilizarse durante el proceso de revisión de solicitudes recibidas para una donación.

#### Implementación

La consulta se implementó en `SolicitudRepository` mediante el método:

```python
def obtener_pendientes_por_donacion(self, donacion_id):
    return self.model.objects.filter(
        donacion_id=donacion_id,
        estado=Solicitud.Estado.PENDIENTE
    )
```

La estructura de la consulta permanece fija: siempre se filtra por una donación determinada y por el estado `PENDIENTE`.

#### Prueba realizada

Se realizó la consulta para la donación con identificador `1`:

```python
solicitudes = repositorio.obtener_pendientes_por_donacion(1)
```

El resultado fue:

```text
<QuerySet [
    <Solicitud: Solicitud 1>,
    <Solicitud: Solicitud 2>
]>

1 PENDIENTE 1 4
2 PENDIENTE 1 5
```

Se encontraron dos solicitudes pendientes asociadas con la donación indicada.

#### SQL generado

```sql
SELECT
    "solicitud"."id_solicitud",
    "solicitud"."id_donacion",
    "solicitud"."id_organizacion_beneficiaria",
    "solicitud"."fecha_solicitud",
    "solicitud"."estado",
    "solicitud"."observacion"
FROM "solicitud"
WHERE (
    "solicitud"."id_donacion" = 1
    AND "solicitud"."estado" = PENDIENTE
);
```

---

## 3. Consultas dinámicas

### 3.1. Filtrado dinámico de donaciones

#### Necesidad de negocio

La consulta permite buscar donaciones utilizando diferentes combinaciones de criterios. Los filtros disponibles corresponden al estado de la donación, categoría, organización donante y fecha límite de retiro.

A diferencia de una consulta directa, no todos los criterios deben estar presentes. El `QuerySet` se construye progresivamente de acuerdo con los parámetros recibidos.

#### Implementación

El método implementado en `DonacionRepository` es:

```python
def filtrar_donaciones(
    self,
    estado=None,
    categoria_id=None,
    organizacion_id=None,
    fecha_limite=None
):
    queryset = self.model.objects.all()

    if estado is not None:
        queryset = queryset.filter(
            estado=estado
        )

    if categoria_id is not None:
        queryset = queryset.filter(
            categoria_id=categoria_id
        )

    if organizacion_id is not None:
        queryset = queryset.filter(
            organizacion_donante_id=organizacion_id
        )

    if fecha_limite is not None:
        queryset = queryset.filter(
            fecha_limite_retiro__lte=fecha_limite
        )

    return queryset
```

#### Prueba con estado y categoría

Se utilizaron los criterios:

```python
resultado = repositorio.filtrar_donaciones(
    estado=Donacion.Estado.DISPONIBLE,
    categoria_id=4
)
```

Resultado:

```text
<QuerySet [<Donacion: Leche de larga duración - 30.00 LITRO>]>

6 Leche de larga duración DISPONIBLE 4 2
```

SQL generado:

```sql
SELECT
    "donacion"."id_donacion",
    "donacion"."id_organizacion_donante",
    "donacion"."id_categoria",
    "donacion"."alimento",
    "donacion"."descripcion",
    "donacion"."cantidad",
    "donacion"."unidad_medida",
    "donacion"."fecha_publicacion",
    "donacion"."fecha_limite_retiro",
    "donacion"."estado"
FROM "donacion"
WHERE (
    "donacion"."estado" = DISPONIBLE
    AND "donacion"."id_categoria" = 4
);
```

#### Prueba con estado y organización donante

Posteriormente se modificaron los criterios:

```python
resultado = repositorio.filtrar_donaciones(
    estado=Donacion.Estado.DISPONIBLE,
    organizacion_id=2
)
```

Resultado:

```text
<QuerySet [
    <Donacion: Manzanas - 25.00 KILOGRAMO>,
    <Donacion: Leche de larga duración - 30.00 LITRO>,
    <Donacion: Atún enlatado - 48.00 UNIDAD>
]>

1 Manzanas DISPONIBLE 1 2
6 Leche de larga duración DISPONIBLE 4 2
4 Atún enlatado DISPONIBLE 5 2
```

SQL generado:

```sql
SELECT
    "donacion"."id_donacion",
    "donacion"."id_organizacion_donante",
    "donacion"."id_categoria",
    "donacion"."alimento",
    "donacion"."descripcion",
    "donacion"."cantidad",
    "donacion"."unidad_medida",
    "donacion"."fecha_publicacion",
    "donacion"."fecha_limite_retiro",
    "donacion"."estado"
FROM "donacion"
WHERE (
    "donacion"."estado" = DISPONIBLE
    AND "donacion"."id_organizacion_donante" = 2
);
```

Las dos ejecuciones muestran que la consulta generada cambia de acuerdo con los criterios proporcionados al método.

---

### 3.2. Filtrado dinámico de solicitudes

#### Necesidad de negocio

El sistema requiere buscar solicitudes utilizando diferentes criterios sin necesitar un método independiente para cada combinación posible.

La consulta permite utilizar opcionalmente el estado, la donación y la organización beneficiaria.

#### Implementación

El método implementado en `SolicitudRepository` es:

```python
def filtrar_solicitudes(
    self,
    estado=None,
    donacion_id=None,
    organizacion_id=None
):
    queryset = self.model.objects.all()

    if estado is not None:
        queryset = queryset.filter(
            estado=estado
        )

    if donacion_id is not None:
        queryset = queryset.filter(
            donacion_id=donacion_id
        )

    if organizacion_id is not None:
        queryset = queryset.filter(
            organizacion_beneficiaria_id=organizacion_id
        )

    return queryset
```

#### Prueba utilizando solamente el estado

```python
resultado = repositorio.filtrar_solicitudes(
    estado=Solicitud.Estado.PENDIENTE
)
```

Resultado:

```text
<QuerySet [
    <Solicitud: Solicitud 1>,
    <Solicitud: Solicitud 2>
]>

1 PENDIENTE 1 4
2 PENDIENTE 1 5
```

SQL generado:

```sql
SELECT
    "solicitud"."id_solicitud",
    "solicitud"."id_donacion",
    "solicitud"."id_organizacion_beneficiaria",
    "solicitud"."fecha_solicitud",
    "solicitud"."estado",
    "solicitud"."observacion"
FROM "solicitud"
WHERE "solicitud"."estado" = PENDIENTE;
```

#### Prueba utilizando estado y donación

Se agregó un segundo criterio a la consulta:

```python
resultado = repositorio.filtrar_solicitudes(
    estado=Solicitud.Estado.PENDIENTE,
    donacion_id=1
)
```

Resultado:

```text
<QuerySet [
    <Solicitud: Solicitud 1>,
    <Solicitud: Solicitud 2>
]>

1 PENDIENTE 1 4
2 PENDIENTE 1 5
```

SQL generado:

```sql
SELECT
    "solicitud"."id_solicitud",
    "solicitud"."id_donacion",
    "solicitud"."id_organizacion_beneficiaria",
    "solicitud"."fecha_solicitud",
    "solicitud"."estado",
    "solicitud"."observacion"
FROM "solicitud"
WHERE (
    "solicitud"."estado" = PENDIENTE
    AND "solicitud"."id_donacion" = 1
);
```

Aunque en este conjunto de datos ambas ejecuciones producen los mismos registros, el SQL generado demuestra que la segunda ejecución incorpora un criterio adicional. Por lo tanto, la estructura final de la consulta depende de los parámetros proporcionados.

---

## 4. Análisis del problema N+1

### 4.1. Escenario sin optimización

Se realizó una prueba para analizar el comportamiento de Django ORM al consultar las donaciones y posteriormente acceder a las relaciones `organizacion_donante` y `categoria`.

La consulta inicial utilizada fue:

```python
donaciones = Donacion.objects.all()

for donacion in donaciones:
    resultados.append(
        (
            donacion.alimento,
            donacion.organizacion_donante.nombre,
            donacion.categoria.nombre,
        )
    )
```

Las relaciones `organizacion_donante` y `categoria` son accedidas después de obtener las donaciones.

La prueba registró:

```text
Cantidad de consultas sin optimizacion: 13
```

La primera consulta obtiene las seis donaciones:

```sql
SELECT
    "donacion"."id_donacion",
    "donacion"."id_organizacion_donante",
    "donacion"."id_categoria",
    "donacion"."alimento",
    "donacion"."descripcion",
    "donacion"."cantidad",
    "donacion"."unidad_medida",
    "donacion"."fecha_publicacion",
    "donacion"."fecha_limite_retiro",
    "donacion"."estado"
FROM "donacion";
```

Posteriormente se ejecutan consultas adicionales para recuperar la organización donante y la categoría de cada registro.

Ejemplo de consulta adicional a `organizacion`:

```sql
SELECT
    "organizacion"."id_organizacion",
    "organizacion"."nombre",
    "organizacion"."tipo",
    "organizacion"."cedula_juridica",
    "organizacion"."descripcion",
    "organizacion"."direccion",
    "organizacion"."telefono",
    "organizacion"."estado",
    "organizacion"."fecha_registro"
FROM "organizacion"
WHERE "organizacion"."id_organizacion" = 2
LIMIT 21;
```

Ejemplo de consulta adicional a `categoria`:

```sql
SELECT
    "categoria"."id_categoria",
    "categoria"."nombre",
    "categoria"."descripcion",
    "categoria"."estado"
FROM "categoria"
WHERE "categoria"."id_categoria" = 1
LIMIT 21;
```

Con los datos de prueba existentes se obtuvieron seis donaciones. Debido a que para cada una se accedió a dos relaciones, el resultado fue:

```text
1 consulta para obtener las donaciones
+ 6 consultas para obtener organizaciones
+ 6 consultas para obtener categorías
------------------------------------------------
13 consultas SQL
```

Este comportamiento representa el problema N+1 en el escenario analizado: recuperar las entidades principales requiere una consulta inicial, pero el acceso posterior a relaciones provoca consultas adicionales.

---

## 5. Optimización del problema N+1

### 5.1. Uso de `select_related()`

Para optimizar la consulta se utilizó `select_related()`:

```python
donaciones = Donacion.objects.select_related(
    "organizacion_donante",
    "categoria"
)

for donacion in donaciones:
    resultados.append(
        (
            donacion.alimento,
            donacion.organizacion_donante.nombre,
            donacion.categoria.nombre,
        )
    )
```

`select_related()` permite recuperar en la consulta inicial las relaciones indicadas mediante operaciones `JOIN`.

### 5.2. Resultado de la optimización

Después de aplicar la optimización, la prueba registró:

```text
Cantidad de consultas con optimizacion: 1
```

El SQL generado fue:

```sql
SELECT
    "donacion"."id_donacion",
    "donacion"."id_organizacion_donante",
    "donacion"."id_categoria",
    "donacion"."alimento",
    "donacion"."descripcion",
    "donacion"."cantidad",
    "donacion"."unidad_medida",
    "donacion"."fecha_publicacion",
    "donacion"."fecha_limite_retiro",
    "donacion"."estado",

    "organizacion"."id_organizacion",
    "organizacion"."nombre",
    "organizacion"."tipo",
    "organizacion"."cedula_juridica",
    "organizacion"."descripcion",
    "organizacion"."direccion",
    "organizacion"."telefono",
    "organizacion"."estado",
    "organizacion"."fecha_registro",

    "categoria"."id_categoria",
    "categoria"."nombre",
    "categoria"."descripcion",
    "categoria"."estado"

FROM "donacion"

INNER JOIN "organizacion"
    ON (
        "donacion"."id_organizacion_donante"
        = "organizacion"."id_organizacion"
    )

INNER JOIN "categoria"
    ON (
        "donacion"."id_categoria"
        = "categoria"."id_categoria"
    );
```

La información de `donacion`, `organizacion` y `categoria` se obtiene ahora mediante una única consulta.

---

## 6. Comparación antes y después

| Escenario | Estrategia | Consultas ejecutadas |
|---|---|---:|
| Sin optimización | Acceso posterior a las relaciones | 13 |
| Con optimización | `select_related()` | 1 |

En el escenario sin optimización se realizaron 13 consultas SQL para recuperar las seis donaciones junto con sus organizaciones y categorías.

Después de aplicar `select_related()`, la misma información pudo recuperarse mediante una única consulta SQL con dos operaciones `INNER JOIN`.

Por lo tanto, la optimización elimina las consultas adicionales generadas durante el acceso a las relaciones.

---

## 7. Equivalencia entre JPA y Django ORM

La guía del laboratorio utiliza conceptos propios de JPA, como JPQL, Criteria/Specifications, `JOIN FETCH` y `@EntityGraph`. Debido a que AlimentaCR utiliza Django y Django ORM como tecnología de persistencia, estos requerimientos fueron implementados mediante mecanismos equivalentes del framework.

La correspondencia utilizada en el proyecto es la siguiente:

| Concepto de JPA | Implementación utilizada en Django ORM |
|---|---|
| JPQL | Consultas directas mediante `QuerySet.filter()` |
| Criteria / Specifications | Construcción dinámica de `QuerySet` mediante filtros opcionales |
| Carga diferida de relaciones | Comportamiento predeterminado de relaciones `ForeignKey` |
| `JOIN FETCH` / `@EntityGraph` | `select_related()` para relaciones `ForeignKey` y `OneToOne` |
| Inspección del SQL generado | `QuerySet.query` y `CaptureQueriesContext` |

Las consultas directas representan operaciones cuyo conjunto de criterios está definido previamente. Por otra parte, las consultas dinámicas construyen progresivamente el `QuerySet` dependiendo de los criterios proporcionados.

Para la corrección del problema N+1, `select_related()` permite que Django genere operaciones `JOIN` y recupere las entidades relacionadas dentro de la consulta principal, evitando las consultas adicionales observadas en el escenario sin optimización.

---

## 8. Pruebas y entorno utilizado

La evidencia del problema N+1 se obtuvo mediante pruebas automatizadas con `pytest` y `pytest-django`.

Para evitar que estas pruebas dependieran de la base de datos utilizada durante el desarrollo, `pytest-django` creó una base temporal denominada:

```text
test_alimentacr
```

Antes de ejecutar las pruebas, el esquema temporal fue preparado mediante Flyway. Se ejecutaron las migraciones:

```text
V1 - crear esquema relacional
V2 - insertar datos prueba
```

Flyway confirmó:

```text
Successfully applied 2 migrations to schema "public",
now at version v2
```

Las pruebas ejecutadas fueron:

```text
test_n_mas_uno_sin_optimizacion
test_n_mas_uno_con_select_related
```

El resultado final fue:

```text
2 passed in 2.49s
```

Al finalizar las pruebas, `pytest-django` eliminó la base de datos temporal.

Este procedimiento permite reproducir el escenario N+1 utilizando el esquema y los datos definidos por las migraciones del proyecto, sin modificar los datos almacenados en la base de desarrollo.

---

## 9. Conclusiones

Las cuatro consultas implementadas permiten cubrir necesidades de búsqueda concretas del dominio de AlimentaCR mediante Django ORM. Las consultas directas mantienen criterios previamente definidos, mientras que las consultas dinámicas permiten construir diferentes combinaciones de filtros sin crear un método independiente para cada combinación.

El análisis de acceso a relaciones permitió identificar un problema N+1 al recuperar donaciones junto con su organización donante y categoría. Con los datos de prueba se ejecutaban 13 consultas SQL.

La utilización de `select_related()` permitió recuperar la misma información mediante una única consulta con operaciones `INNER JOIN`, reduciendo las 13 consultas observadas a una sola consulta.

La evidencia obtenida mediante el SQL generado y las pruebas automatizadas permite verificar tanto el comportamiento inicial como el resultado de la optimización aplicada.