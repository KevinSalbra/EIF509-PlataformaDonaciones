# Propuesta de Dominio — AlimentaCR

## 1. Identificación

**Sistema:** AlimentaCR  
**Integrantes:** Kevin Salazar Bravo y Kimberley Gómez Quesada

---

## 2. El negocio

### Descripción del negocio

AlimentaCR es una plataforma orientada a facilitar la gestión de donaciones de alimentos entre empresas u organizaciones donantes y organizaciones beneficiarias en Costa Rica. Está dirigida a supermercados, agricultores, restaurantes, panaderías y otros comercios que generan excedentes de alimentos todavía aptos para el consumo, así como a asociaciones de desarrollo, comedores comunitarios, hogares de adultos mayores, albergues y organizaciones sin fines de lucro que requieran estos recursos.

Actualmente, muchas donaciones se coordinan mediante llamadas telefónicas, mensajes de WhatsApp o contactos personales, e incluso algunos excedentes no llegan a donarse. Esto dificulta la asignación organizada de los alimentos, el seguimiento del proceso y el aprovechamiento oportuno de productos que todavía pueden utilizarse. AlimentaCR busca centralizar este proceso mediante una plataforma que permita publicar, solicitar, asignar y registrar la entrega de donaciones.

### Actores

#### Administrador

Responsable de administrar la plataforma. Puede revisar y gestionar organizaciones, administrar categorías de alimentos, gestionar estados de usuarios y consultar información general necesaria para el funcionamiento del sistema.

#### Representante de organización donante

Usuario asociado a una empresa u organización que ofrece alimentos. Puede publicar y administrar sus donaciones, consultar las solicitudes recibidas, aceptar o rechazar solicitudes y participar en la coordinación y confirmación de las entregas.

#### Representante de organización beneficiaria

Usuario asociado a una organización que recibe donaciones. Puede consultar donaciones disponibles, realizar y cancelar solicitudes pendientes, consultar el estado de sus solicitudes y confirmar la recepción de una entrega.

---

## 3. Entidades de negocio

### Usuario

Representa a una persona que utiliza la plataforma.

**Datos principales:** identificador, nombre, correo electrónico, contraseña, teléfono, rol y estado.

**Relación:** un Usuario pertenece a una Organización y puede generar múltiples registros en la Bitácora.

### Organización

Representa una empresa u organización participante del sistema, ya sea donante o beneficiaria.

**Datos principales:** identificador, nombre, tipo, cédula jurídica, descripción, dirección, teléfono y estado de aprobación.

**Relaciones:** una Organización puede tener varios Usuarios. Una organización donante puede publicar múltiples Donaciones y una organización beneficiaria puede realizar múltiples Solicitudes.

### Categoría

Permite clasificar las donaciones según el tipo de alimento.

**Datos principales:** identificador, nombre, descripción y estado.

**Relación:** una Categoría puede clasificar múltiples Donaciones.

### Donación

Representa una publicación de alimentos disponibles para ser donados.

**Datos principales:** identificador, organización donante, categoría, nombre o descripción del alimento, cantidad, unidad de medida, fecha de publicación, fecha límite de retiro y estado.

**Relaciones:** una Donación pertenece a una Organización donante y a una Categoría. Una Donación puede recibir múltiples Solicitudes, pero solo una de ellas puede ser aceptada.

### Solicitud

Representa el interés de una organización beneficiaria por recibir una donación.

**Datos principales:** identificador, donación, organización solicitante, fecha, estado y observación.

**Relaciones:** una Solicitud pertenece a una Donación y a una Organización beneficiaria. Una Solicitud aceptada puede originar una Entrega.

### Entrega

Registra la coordinación y confirmación de una donación que fue asignada.

**Datos principales:** identificador, solicitud aceptada, fecha acordada, lugar, observaciones, confirmación del donante, confirmación del beneficiario y estado.

**Relación:** una Entrega corresponde a una única Solicitud aceptada.

### Bitácora

Registra acciones y eventos relevantes ocurridos dentro del sistema.

**Datos principales:** identificador, usuario responsable, acción realizada, fecha y hora, descripción, entidad afectada y datos adicionales del evento.

**Relación:** un Usuario puede generar múltiples registros en la Bitácora.

### Relaciones principales

- Una Organización puede tener muchos Usuarios.
- Una Organización donante puede publicar muchas Donaciones.
- Una Organización beneficiaria puede realizar muchas Solicitudes.
- Una Categoría puede clasificar muchas Donaciones.
- Una Donación puede recibir muchas Solicitudes.
- Una Solicitud pertenece a una única Donación.
- Solo una Solicitud por Donación puede ser aceptada.
- Una Solicitud aceptada puede generar una Entrega.
- Una Entrega corresponde a una única Solicitud aceptada.
- Un Usuario puede generar muchos registros de Bitácora.

### Subdominio documental candidato

La Bitácora se plantea como subdominio documental candidato. Cada registro almacenará información común, como el usuario responsable, la fecha, la acción realizada y la entidad afectada, pero podrá contener datos adicionales diferentes según el tipo de evento. Esta variabilidad permite tratar el historial de eventos como información documental en una etapa posterior del proyecto.

---

## 4. Procesos de negocio

Los siguientes procesos representan el flujo principal previsto para AlimentaCR. Los dos primeros corresponden a los procesos inicialmente definidos para el Laboratorio 1; los demás amplían el dominio para reflejar las operaciones principales que deberá soportar el sistema durante el curso.

### Proceso 1: Publicar una donación

El representante de una organización donante autenticado registra una nueva donación indicando el alimento, categoría, cantidad, unidad de medida, descripción y fecha límite de retiro. El sistema verifica que la organización esté aprobada, que la categoría esté activa, que los campos obligatorios sean válidos, que la cantidad sea mayor que cero y que la fecha límite sea posterior a la fecha actual. Si las validaciones se cumplen, la donación se registra con estado `DISPONIBLE` y se genera el evento correspondiente en la Bitácora.

Como procesamiento adicional, el sistema puede determinar los días restantes para retirar la donación a partir de la diferencia entre la fecha límite y la fecha actual.

**Reglas principales:**

- Solo una organización donante aprobada puede publicar donaciones.
- La cantidad debe ser mayor que cero.
- La categoría seleccionada debe estar activa.
- La fecha límite de retiro debe ser posterior a la fecha actual.
- Toda nueva donación inicia en estado `DISPONIBLE`.

### Proceso 2: Aceptar una solicitud y asignar la donación

El representante de la organización donante consulta las solicitudes pendientes asociadas a una de sus donaciones y selecciona una para aceptarla. El sistema verifica que la solicitud continúe en estado `PENDIENTE`, que pertenezca a la donación correspondiente, que la donación permanezca disponible y que no exista otra solicitud previamente aceptada.

Al aceptar la solicitud, esta cambia a estado `ACEPTADA`, las demás solicitudes pendientes de la misma donación pasan a `RECHAZADA`, la donación cambia a estado `ASIGNADA`, se crea el registro inicial de Entrega y se registra la operación en la Bitácora.

Todos estos cambios deben ejecutarse como una única transacción. Si alguno falla, ninguno de los cambios debe quedar aplicado.

**Reglas principales:**

- Solo el donante propietario de la donación puede aceptar una solicitud.
- Una donación solo puede tener una solicitud aceptada.
- Solo una solicitud en estado `PENDIENTE` puede aceptarse.
- Una donación debe estar `DISPONIBLE` para poder asignarse.
- La Entrega únicamente puede generarse a partir de una Solicitud aceptada.

### Proceso 3: Solicitar una donación

El representante de una organización beneficiaria consulta las donaciones disponibles y selecciona aquella que desea solicitar. El sistema valida que la organización beneficiaria esté aprobada, que la donación continúe disponible y que la misma organización no tenga una solicitud pendiente para esa donación. Si las condiciones se cumplen, se crea la Solicitud con estado `PENDIENTE` y se registra el evento en la Bitácora.

**Reglas principales:**

- Solo una organización beneficiaria aprobada puede solicitar donaciones.
- Solo pueden solicitarse donaciones en estado `DISPONIBLE`.
- Una organización no puede tener dos solicitudes pendientes sobre la misma donación.
- La organización beneficiaria no puede solicitar una donación publicada por ella misma.

### Proceso 4: Cancelar una solicitud

El representante de una organización beneficiaria puede cancelar una solicitud realizada previamente mientras esta continúe pendiente. El sistema verifica que la solicitud pertenezca a su organización y que su estado sea `PENDIENTE`. Una vez cancelada, cambia a estado `CANCELADA` y el evento queda registrado en la Bitácora.

**Reglas principales:**

- Solo la organización que creó la solicitud puede cancelarla.
- Únicamente pueden cancelarse solicitudes pendientes.
- Una solicitud aceptada, rechazada o previamente cancelada no puede volver a cancelarse.

### Proceso 5: Coordinar una entrega

Después de aceptar una solicitud, se dispone de un registro de Entrega asociado a ella. Las organizaciones involucradas podrán registrar o consultar la fecha acordada, el lugar y las observaciones necesarias para coordinar la entrega. El sistema valida que la entrega corresponda a una solicitud aceptada y que la fecha acordada no sea anterior a la fecha actual.

**Reglas principales:**

- Solo las organizaciones involucradas en la donación pueden acceder a la coordinación de la entrega.
- La Entrega debe estar asociada a una Solicitud aceptada.
- La fecha acordada debe ser válida.
- Una donación no puede tener múltiples entregas activas.

### Proceso 6: Confirmar la entrega y recepción

Una vez realizado el intercambio, el representante donante confirma que realizó la entrega y el representante beneficiario confirma que recibió los alimentos. El sistema registra ambas confirmaciones. Cuando se cumplen las confirmaciones requeridas, la Entrega cambia a estado `FINALIZADA`, la Donación pasa a estado `ENTREGADA` y se registra el evento en la Bitácora.

**Reglas principales:**

- Solo el donante involucrado puede confirmar la entrega.
- Solo el beneficiario involucrado puede confirmar la recepción.
- Una entrega ya finalizada no puede confirmarse nuevamente.
- La donación solo puede marcarse como entregada cuando el proceso de entrega haya finalizado correctamente.

### Proceso 7: Gestionar organizaciones

Cuando una organización se registra en la plataforma, permanece pendiente de aprobación hasta que un Administrador revise su información. El Administrador puede aprobar o rechazar la organización. Una organización aprobada puede utilizar las operaciones correspondientes a su tipo; una organización no aprobada no puede publicar ni solicitar donaciones.

**Reglas principales:**

- Solo el Administrador puede aprobar o rechazar organizaciones.
- Una organización debe tener la información obligatoria completa antes de ser aprobada.
- Una organización no aprobada no puede participar en los procesos de donación.
- El tipo de organización determina las operaciones de negocio que puede realizar.

### Proceso 8: Gestionar categorías de alimentos

El Administrador puede registrar, modificar y desactivar las categorías utilizadas para clasificar las donaciones. Las categorías permiten mantener una clasificación uniforme de los alimentos publicados.

**Reglas principales:**

- Solo el Administrador puede gestionar categorías.
- El nombre de una categoría debe ser único.
- Una categoría inactiva no puede utilizarse en nuevas donaciones.
- La desactivación de una categoría no elimina las donaciones históricas asociadas a ella.

### Proceso 9: Consultar donaciones disponibles

Los representantes de organizaciones beneficiarias pueden consultar las donaciones que se encuentren disponibles y utilizar criterios básicos de filtrado, como categoría o fecha límite de retiro. El sistema solo debe presentar como solicitables aquellas donaciones que continúen vigentes y disponibles.

**Reglas principales:**

- Las donaciones asignadas, entregadas o canceladas no deben aparecer como disponibles para nuevas solicitudes.
- Las donaciones cuya fecha límite haya vencido no pueden recibir nuevas solicitudes.
- Los filtros de consulta no modifican la información de las donaciones.

### Proceso 10: Consultar historial de operaciones

Los usuarios podrán consultar la información histórica relacionada con las operaciones que les corresponden según su rol, como donaciones publicadas, solicitudes enviadas o recibidas y entregas realizadas. El historial permite conservar trazabilidad sin modificar los registros originales.

**Reglas principales:**

- Cada usuario solo puede consultar la información permitida por su rol y organización.
- La consulta del historial no permite alterar eventos ya finalizados.
- Los eventos relevantes del negocio se registran en la Bitácora.

---

## 5. Alcance

### Dentro del alcance

El sistema permitirá registrar y administrar organizaciones donantes y beneficiarias, gestionar usuarios con diferentes roles, publicar y consultar donaciones de alimentos, administrar categorías, enviar y cancelar solicitudes, aceptar o rechazar solicitudes y registrar la coordinación y confirmación de las entregas. También incluirá el manejo de estados de donaciones, solicitudes y entregas, autenticación de usuarios, consulta de historiales y una bitácora de las operaciones relevantes. La solución se implementará como una aplicación web apoyada por una API REST desarrollada con Python y Django REST Framework.

### Fuera del alcance

El sistema no incluirá pagos ni pasarelas de pago, facturación electrónica, aplicación móvil nativa, administración completa del inventario de las organizaciones, entregas parciales de una misma donación, gestión física del transporte, cálculo de rutas, GPS o geolocalización en tiempo real. Tampoco se contemplan chat interno, integración con WhatsApp, SMS u otros servicios de mensajería, inteligencia artificial, sistemas de reputación, validaciones automáticas mediante sistemas gubernamentales ni controles sanitarios de los alimentos. Estas funcionalidades se excluyen para mantener un alcance realista para un proyecto universitario desarrollado por dos personas durante el curso.

---

## 6. Reglas y restricciones generales del dominio

- Cada Usuario pertenece a una Organización.
- Una Organización se registra como donante o beneficiaria.
- Solo las Organizaciones aprobadas pueden participar en los procesos principales.
- Una Donación pertenece a una única Organización donante.
- Una Donación se asigna completamente a una única Organización beneficiaria.
- No se contemplan entregas parciales ni división de una Donación entre varios beneficiarios.
- Una Donación puede recibir varias Solicitudes, pero solo una puede ser aceptada.
- Una Solicitud aceptada es requisito para generar y completar una Entrega.
- Una Donación asignada deja de aceptar nuevas Solicitudes.
- La plataforma registra la coordinación de la Entrega, pero no administra el transporte físico.
- La Organización donante es responsable de proporcionar información correcta sobre los alimentos ofrecidos y de que sean aptos para el consumo.
- Las acciones relevantes del negocio deben conservar trazabilidad mediante la Bitácora.

---

## 7. Estados principales del dominio

### Donación

- `DISPONIBLE`: puede recibir solicitudes.
- `ASIGNADA`: una solicitud fue aceptada.
- `ENTREGADA`: la entrega fue completada.
- `CANCELADA`: la donación fue retirada del proceso.
- `VENCIDA`: superó su fecha límite sin ser asignada.

### Solicitud

- `PENDIENTE`: espera decisión del donante.
- `ACEPTADA`: fue seleccionada para recibir la donación.
- `RECHAZADA`: no fue seleccionada.
- `CANCELADA`: fue retirada por la organización beneficiaria.

### Entrega

- `PENDIENTE`: fue creada y requiere coordinación o confirmación.
- `FINALIZADA`: la entrega fue completada y confirmada.
- `CANCELADA`: el proceso de entrega fue cancelado cuando las reglas del negocio lo permitan.

### Organización

- `PENDIENTE`: espera revisión administrativa.
- `APROBADA`: puede operar en la plataforma.
- `RECHAZADA`: su registro no fue aprobado.
- `INACTIVA`: tiene restringida temporalmente la participación en nuevos procesos.

---

## 8. Consideraciones para la evolución del proyecto

La definición de este dominio representa el alcance previsto de AlimentaCR para el curso y podrá evolucionar de forma incremental conforme se desarrollen los laboratorios. Cualquier funcionalidad adicional deberá respetar las entidades, reglas y responsabilidades establecidas en este documento y mantenerse dentro de un alcance viable para el equipo.

Las funcionalidades que no forman parte del flujo principal —publicar una donación, solicitarla, asignarla y completar su entrega— deberán evaluarse antes de incorporarse para evitar aumentar innecesariamente la complejidad del sistema.
