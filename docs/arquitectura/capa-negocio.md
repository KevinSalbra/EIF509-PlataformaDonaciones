# Capa de negocio y validación -- Laboratorio 4

## 1. Propósito

Este documento describe los avances realizados en la capa de negocio de
AlimentaCR durante el desarrollo del Laboratorio 4. En esta etapa se
trabajó en el proceso de publicación de donaciones, la aplicación del
patrón Specification, la integración con la capa de presentación y la
bitácora, así como en el fortalecimiento de las pruebas automatizadas de
los procesos de negocio.

También se realizaron ajustes en la infraestructura de pruebas para
separar correctamente las pruebas unitarias de las pruebas de
integración, se incorporó una prueba real de rollback para el proceso
transaccional de aceptación de solicitudes y se configuró la
verificación automática de cobertura dentro del flujo de integración
continua.

## 2. Proceso de publicación de donaciones

Se implementó el proceso de negocio encargado de registrar nuevas
donaciones en AlimentaCR. La coordinación de este caso de uso se
encuentra en `DonacionService`, dentro de la capa `business`.

El servicio recibe los datos requeridos para la publicación y consulta
los repositorios correspondientes para obtener la organización donante y
la categoría seleccionada. Antes de persistir la nueva donación se
comprueban las reglas definidas por el dominio.

Las reglas contempladas son:

-   La organización indicada debe existir.
-   La organización debe ser de tipo `DONANTE`.
-   La organización debe encontrarse en estado `APROBADA`.
-   La categoría indicada debe existir.
-   La categoría debe encontrarse en estado `ACTIVA`.
-   La cantidad de alimento debe ser mayor que cero.
-   La fecha límite de retiro debe ser posterior a la fecha actual.
-   Toda nueva donación debe crearse inicialmente en estado
    `DISPONIBLE`.

Cuando las validaciones son satisfactorias, se construye la entidad
`Donacion`, se establece la fecha de publicación y se utiliza
`DonacionRepository` para persistirla.

## 3. Excepciones de negocio

Para representar de forma explícita los incumplimientos de las reglas
del dominio se incorporaron excepciones específicas en
`business/exceptions.py`.

Para el proceso de publicación de donaciones se agregaron:

-   `OrganizacionNoExisteError`
-   `OrganizacionNoAutorizadaError`
-   `CategoriaNoExisteError`
-   `CategoriaInactivaError`
-   `CantidadInvalidaError`
-   `FechaLimiteInvalidaError`

El uso de excepciones propias permite diferenciar los errores esperados
del negocio de errores técnicos o inesperados. Asimismo, facilita que la
capa de presentación transforme posteriormente cada situación en una
respuesta HTTP apropiada sin trasladar esa responsabilidad al servicio.

## 4. Aplicación del patrón Specification

Las reglas asociadas a la publicación de una donación se separaron
mediante el patrón de diseño **Specification**.

La implementación se encuentra en:

`business/specifications/donacion_specifications.py`

Se definieron las siguientes especificaciones:

-   `OrganizacionPuedeDonarSpecification`
-   `CategoriaActivaSpecification`
-   `CantidadPositivaSpecification`
-   `FechaLimiteFuturaSpecification`

Cada especificación encapsula una regla concreta y genera la excepción
de negocio correspondiente cuando la condición evaluada no se cumple.

### 4.1 Justificación

La publicación de una donación depende de varias condiciones
independientes. Mantener todas estas validaciones directamente dentro de
`DonacionService` provocaría que el servicio acumulara estructuras
condicionales y mezclara la coordinación del proceso con la
implementación detallada de cada regla.

Specification permite mantener cada condición separada y con una
responsabilidad específica. De esta forma, `DonacionService` conserva la
responsabilidad de coordinar el caso de uso, mientras las
especificaciones se encargan de las reglas individuales.

Esta organización también facilita la incorporación de nuevas reglas y
la realización de pruebas independientes sobre cada condición.

## 5. Integración con la capa de presentación

Para controlar los datos utilizados por el proceso de publicación se
incorporaron serializers de Django REST Framework.

Entre los componentes utilizados se encuentran:

-   `PublicarDonacionRequestSerializer`
-   `DonacionResponseSerializer`
-   `PublicarDonacionView`

El serializer de entrada se encarga de validar aspectos estructurales,
como los tipos de datos, identificadores, longitudes, unidad de medida y
formato de fecha.

Las reglas propias del dominio, como determinar si una organización está
autorizada para donar o si una categoría se encuentra activa, permanecen
en la capa `business`.

`PublicarDonacionView` recibe la solicitud HTTP, valida la entrada,
invoca el servicio de negocio y transforma las excepciones conocidas en
respuestas HTTP.

## 6. Registro de la publicación en la bitácora

Una vez publicada correctamente una donación, el proceso registra el
evento correspondiente en la bitácora almacenada en MongoDB mediante
`BitacoraRepository`.

Durante la validación manual del endpoint se detectó que el esquema de
la colección utiliza un catálogo específico para identificar las
entidades. El evento fue ajustado para registrar:

`DONACION`

como valor de la entidad.

Después de la corrección se comprobó el flujo completo: la donación fue
persistida en PostgreSQL y el evento `DONACION_PUBLICADA` fue registrado
correctamente en la colección `eventos` de la bitácora.

## 7. Pruebas unitarias del proceso de publicación

Se incorporaron pruebas unitarias para `DonacionService` en:

`main/test/cr/ac/una/alimentaCR/business/test_donacion_service.py`

Estas pruebas utilizan mocks para aislar la lógica de negocio de
PostgreSQL y MongoDB.

Se validaron los siguientes escenarios:

1.  Publicación exitosa de una donación.
2.  Organización inexistente.
3.  Organización que no es de tipo donante.
4.  Organización donante que no se encuentra aprobada.
5.  Categoría inexistente.
6.  Categoría inactiva.
7.  Cantidad igual a cero.
8.  Fecha límite que no es posterior a la fecha actual.

De esta forma se comprueba tanto el flujo exitoso como las principales
reglas implementadas mediante Specification.

## 8. Separación entre pruebas unitarias y pruebas de integración

Durante la incorporación de las pruebas de negocio se identificó que la
fixture `preparar_esquema_flyway` estaba configurada para ejecutarse
automáticamente en todas las pruebas.

Esto provocaba que incluso las pruebas unitarias basadas exclusivamente
en mocks intentaran preparar PostgreSQL mediante Testcontainers y
Flyway.

Para separar ambos tipos de pruebas se eliminó el comportamiento global
de la fixture y se incorporó un `conftest.py` específico en:

`main/test/cr/ac/una/alimentaCR/data/conftest.py`

En este archivo se solicita automáticamente `preparar_esquema_flyway`
para las pruebas de persistencia.

Como resultado:

-   Las pruebas unitarias de negocio pueden ejecutarse sin depender de
    PostgreSQL.
-   Las pruebas de integración de repositorios continúan utilizando
    Testcontainers y Flyway.
-   La preparación de infraestructura se realiza únicamente donde es
    necesaria.
-   Las pruebas existentes de persistencia continúan funcionando con el
    esquema real creado mediante Flyway.

## 9. Ampliación de las pruebas de SolicitudService

También se ampliaron las pruebas unitarias del proceso de aceptación de
solicitudes mediante:

`main/test/cr/ac/una/alimentaCR/business/test_solicitud_service.py`

El proceso utiliza `@transaction.atomic`. Debido a que el decorador
inicia una transacción de Django, las pruebas puramente unitarias
ejecutan la función interna mediante `.__wrapped__`, permitiendo probar
la lógica con repositorios simulados y sin depender de PostgreSQL.

La transacción real se valida de manera independiente mediante una
prueba de integración.

Los escenarios comprobados incluyen:

-   Aceptación exitosa de una solicitud.
-   Solicitud inexistente.
-   Solicitud que ya no se encuentra pendiente.
-   Usuario que no pertenece a la organización donante.
-   Usuario inexistente.
-   Donación que no se encuentra disponible.

En el flujo exitoso se verifica que la solicitud seleccionada cambie a
`ACEPTADA`, las demás solicitudes pendientes de la donación cambien a
`RECHAZADA`, la donación pase a `ASIGNADA` y se genere una entrega en
estado `PENDIENTE`.

## 10. Validación del rollback transaccional

Para comprobar el comportamiento real de `@transaction.atomic` se
incorporó una prueba de integración específica:

`main/test/cr/ac/una/alimentaCR/business/test_solicitud_service_rollback.py`

Esta prueba utiliza PostgreSQL mediante Testcontainers y prepara el
esquema utilizando las migraciones de Flyway.

La prueba crea datos controlados para ejecutar el proceso de aceptación
de una solicitud y utiliza un repositorio de entrega de prueba que
genera deliberadamente un `RuntimeError` cuando el servicio intenta
guardar la entrega.

El error se produce después de que el proceso ha intentado realizar las
modificaciones anteriores:

``` text
Solicitud seleccionada -> ACEPTADA
Otra solicitud         -> RECHAZADA
Donación                -> ASIGNADA
Crear entrega           -> ERROR
                              |
                              v
                           ROLLBACK
```

Después de producirse la excepción, las entidades se consultan
nuevamente desde PostgreSQL para verificar su estado persistido.

El resultado esperado y comprobado es:

``` text
Solicitud seleccionada -> PENDIENTE
Otra solicitud         -> PENDIENTE
Donación                -> DISPONIBLE
Entrega                 -> NO EXISTE
```

También se verifica que la bitácora no sea invocada cuando falla la
parte transaccional relacional.

Esta prueba demuestra que el proceso multiescritura no deja cambios
parciales en PostgreSQL cuando falla la creación de la entrega.

## 11. Cobertura de código

Se incorporó `pytest-cov` para medir la cobertura de la capa de negocio.

La ejecución de las pruebas produjo los siguientes resultados:

``` text
DonacionService                         100%
SolicitudService                         96%
donacion_specifications.py               97%
solicitud_states.py                      90%
------------------------------------------------
Cobertura total de business              96%
```

La cobertura obtenida supera el umbral mínimo del 70 % establecido para
el laboratorio.

El objetivo de las pruebas no es alcanzar artificialmente un 100 %, sino
cubrir los flujos principales, las reglas del negocio y los escenarios
de error relevantes.

## 12. Integración continua

El workflow de GitHub Actions fue actualizado para incorporar la
medición y validación automática de cobertura.

El paso de pruebas ejecuta:

``` bash
python -m pytest \
  --cov=cr.ac.una.alimentaCR.business \
  --cov-report=term-missing \
  --cov-fail-under=70 \
  -v
```

La opción `--cov-fail-under=70` hace que el pipeline falle
automáticamente si futuras modificaciones reducen la cobertura de la
capa de negocio por debajo del porcentaje mínimo requerido.

El workflow conserva la instalación de dependencias, la configuración de
Python, el servicio PostgreSQL y la validación de la configuración de
Django mediante `manage.py check`.

## 13. Estado del avance

Con estos cambios se incorporó el proceso de publicación de donaciones a
la capa de negocio, junto con sus reglas, excepciones, especificaciones,
entrada y salida desde la capa de presentación y registro en la
bitácora.

También se fortaleció la validación automatizada de la capa `business`.
Las pruebas unitarias quedaron separadas de las pruebas que requieren
infraestructura, se amplió la cobertura de los dos servicios de negocio,
se comprobó el rollback real del proceso multiescritura mediante
PostgreSQL/Testcontainers y se agregó al CI un umbral mínimo de
cobertura.

Al finalizar esta validación, la capa `business` presenta una cobertura
total del **96 %**.
