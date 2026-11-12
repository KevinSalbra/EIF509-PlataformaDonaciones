# ADR-004 · Definición del dominio y alcance de AlimentaCR

**Responsables:** Kevin Salazar Bravo y Kimberley Gómez Quesada

## Contexto

En Costa Rica, numerosas organizaciones, comercios y productores generan excedentes de alimentos que todavía son aptos para el consumo. Al mismo tiempo, organizaciones beneficiarias como comedores comunitarios, asociaciones de desarrollo, hogares de adultos mayores y albergues necesitan acceder a este tipo de recursos.

La coordinación de estas donaciones puede depender de llamadas telefónicas, mensajes de WhatsApp o contactos personales. Esto dificulta publicar los alimentos disponibles, conocer quién los solicita, seleccionar una organización beneficiaria y mantener trazabilidad sobre la entrega realizada.

El proyecto se desarrolla como parte del curso EIF509 por un equipo de dos personas durante un periodo académico limitado. Por esta razón, era necesario definir un dominio que permitiera implementar un proceso de negocio completo y demostrable sin incorporar responsabilidades externas que aumentaran excesivamente la complejidad, como transporte, controles sanitarios, pagos o geolocalización.

También era necesario establecer claramente qué responsabilidades pertenecen a AlimentaCR y cuáles permanecen en las organizaciones participantes.

## Decisión

AlimentaCR se define como una plataforma web para administrar el ciclo de donación de alimentos entre organizaciones donantes y organizaciones beneficiarias.

El flujo principal del dominio comprende:

1. Registrar y aprobar organizaciones participantes.
2. Administrar usuarios y categorías de alimentos.
3. Publicar donaciones.
4. Consultar donaciones disponibles.
5. Crear y cancelar solicitudes.
6. Aceptar una solicitud y rechazar las restantes.
7. Coordinar y confirmar la entrega.
8. Conservar trazabilidad mediante una bitácora de eventos.

Los actores principales son:

- Administrador.
- Representante de organización donante.
- Representante de organización beneficiaria.

El sistema administrará las entidades Organización, Usuario, Categoría, Donación, Solicitud y Entrega, junto con una bitácora documental de los eventos relevantes.

Cada donación será asignada completamente a una única organización beneficiaria. No se contemplan entregas parciales ni la división de una donación entre varias organizaciones. Una donación puede recibir varias solicitudes, pero solamente una puede ser aceptada.

AlimentaCR registrará la coordinación y confirmación de las entregas, pero no administrará el transporte físico de los alimentos. La organización donante será responsable de proporcionar información correcta y de garantizar que los alimentos ofrecidos sean aptos para el consumo.

Quedan fuera del alcance:

- Pagos y facturación electrónica.
- Aplicaciones móviles nativas.
- Administración completa de inventarios.
- Entregas parciales.
- Gestión física del transporte.
- Cálculo de rutas y geolocalización en tiempo real.
- Chat interno e integración con servicios de mensajería.
- Controles sanitarios automatizados.
- Validaciones con sistemas gubernamentales.
- Inteligencia artificial y sistemas de reputación.

El detalle de las entidades, procesos, reglas y estados del dominio se mantiene en `docs/Propuesta-Dominio.md`.

## Alternativas consideradas

### Plataforma integral de logística y distribución

Esta alternativa incluía transporte, asignación de vehículos, cálculo de rutas, geolocalización y seguimiento de las entregas en tiempo real.

No fue seleccionada porque incorporaba responsabilidades logísticas externas al objetivo principal del sistema. Además, requería integrar mapas, ubicación, planificación de rutas y posiblemente aplicaciones móviles, lo cual excedía el tiempo y los recursos disponibles para un equipo de dos personas.

### Tablón básico de publicaciones

Esta alternativa consistía únicamente en permitir que las organizaciones donantes publicaran alimentos disponibles y que las organizaciones beneficiarias consultaran la información de contacto.

No fue seleccionada porque mantendría la coordinación principal fuera de la plataforma. No permitiría administrar solicitudes, seleccionar una organización beneficiaria, confirmar entregas ni conservar trazabilidad completa del proceso.

### Plataforma genérica para cualquier tipo de donación

Esta alternativa permitía gestionar alimentos, ropa, dinero, medicamentos y otros recursos mediante un modelo común.

No fue seleccionada porque cada tipo de donación posee reglas, riesgos y procesos diferentes. Limitar el dominio a alimentos permite definir reglas específicas sobre cantidades, categorías, fechas límite y condiciones de entrega.

### Gestión del ciclo completo de donaciones de alimentos

Esta fue la alternativa seleccionada. Permite cubrir un proceso de negocio completo —publicar, solicitar, asignar y entregar— manteniendo límites claros y un alcance viable para el proyecto académico.

## Consecuencias

### Positivas

- El sistema resuelve un proceso de negocio completo y demostrable de extremo a extremo.
- Los actores y sus responsabilidades quedan claramente definidos.
- Las reglas de publicación, solicitud, asignación y entrega pueden implementarse y probarse de manera independiente.
- La plataforma conserva trazabilidad sobre las operaciones relevantes.
- El alcance es viable para un equipo de dos personas durante el periodo académico.
- La exclusión de transporte, pagos y controles sanitarios reduce dependencias con servicios externos.
- La especialización en alimentos permite utilizar categorías, cantidades, unidades de medida y fechas límite propias del dominio.

### Negativas

- La coordinación física de la entrega todavía requiere acuerdos entre las organizaciones.
- El sistema no verifica automáticamente la condición sanitaria de los alimentos.
- Una donación no puede dividirse entre varias organizaciones beneficiarias.
- La plataforma no optimiza rutas ni asigna medios de transporte.
- Algunas comunicaciones pueden seguir realizándose mediante canales externos.
- Ampliar el sistema a otros tipos de donaciones requeriría revisar las entidades y reglas actuales.

### Neutras

- Las nuevas funcionalidades deberán evaluarse antes de incorporarse para evitar que el sistema pierda sus límites de dominio.
- La evolución del proyecto debe mantener como flujo central la publicación, solicitud, asignación y entrega de alimentos.
- Los detalles operativos del dominio permanecen documentados en `docs/Propuesta-Dominio.md`, mientras que este ADR conserva únicamente la decisión y su justificación.