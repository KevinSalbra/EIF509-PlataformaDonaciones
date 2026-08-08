ADR-001 · Selección de Python y Django REST Framework como stack backend

Estado

Aceptada

Fecha: 08/08/2026Responsables: Kevin Salazar Bravo y Kimberley Gómez Quesada

Contexto

El curso propone como stack tecnológico de referencia Java 21, Spring Boot 3 y Gradle para el desarrollo del backend. Sin embargo, estas tecnologías son desconocidas para ambos integrantes del equipo. Aunque aprender el stack durante el desarrollo es posible, hacerlo implicaría dedicar una parte importante del tiempo disponible a la curva de aprendizaje, configuración y resolución de problemas propios de tecnologías nuevas para el equipo.

El proyecto será desarrollado por dos estudiantes durante un periodo académico limitado y de forma paralela a otras responsabilidades universitarias. Por esta razón, se consideró conveniente utilizar tecnologías con las que el equipo tenga experiencia previa, de manera que el esfuerzo pueda concentrarse principalmente en los objetivos del curso: arquitectura por capas, lógica de negocio, persistencia de datos, integración continua y calidad del proyecto.

Antes de tomar la decisión, se solicitó autorización al profesor para utilizar un stack alternativo equivalente. En dicha solicitud se presentaron dos opciones: TypeScript con NestJS y Python con Django REST Framework. En ambos casos se planteó mantener la separación entre presentación, lógica de negocio y acceso a datos, así como PostgreSQL, MongoDB, pruebas automatizadas y GitHub Actions según las necesidades de los laboratorios.

Decisión

Se utilizará Python con Django REST Framework (DRF) como tecnología principal para desarrollar el backend y la API REST de AlimentaCR.

El stack previsto estará compuesto por:

Python como lenguaje de programación.

Django como framework base.

Django REST Framework para la construcción de la API REST.

Django ORM para el acceso y persistencia de datos relacionales.

PostgreSQL como base de datos relacional.

MongoDB para los componentes documentales que sean requeridos posteriormente en el curso.

pytest para pruebas automatizadas.

GitHub Actions para integración continua.

Aunque Django posee una estructura propia y permite concentrar parte de la lógica dentro de sus aplicaciones, el proyecto mantendrá una separación explícita de responsabilidades para cumplir con la arquitectura solicitada en el curso. La capa de presentación contendrá los componentes relacionados con la API, la lógica de negocio se mantendrá separada en servicios y la persistencia se realizará mediante los modelos, ORM y componentes de acceso a datos correspondientes.

La decisión busca utilizar un stack conocido por el equipo sin modificar los objetivos arquitectónicos ni los requisitos establecidos para los laboratorios.

Alternativas consideradas

Java 21, Spring Boot 3 y Gradle

Esta corresponde al stack tecnológico de referencia propuesto por el curso. Su principal ventaja es que los ejemplos, instrucciones y materiales proporcionados por el profesor estarán directamente alineados con estas tecnologías.

No fue seleccionado debido a que Java 21, Spring Boot y Gradle representan tecnologías desconocidas para ambos integrantes. Adoptarlas implicaría asumir simultáneamente la curva de aprendizaje del stack y el desarrollo del proyecto. Para un equipo de dos personas y un periodo académico limitado, esto podría aumentar el tiempo dedicado a configuración y aprendizaje técnico en lugar de concentrarlo en los conceptos arquitectónicos y de negocio evaluados durante el curso.

TypeScript y NestJS

NestJS fue considerada como una alternativa debido a que proporciona una estructura organizada para desarrollar aplicaciones backend y APIs REST con TypeScript. La propuesta contemplaba utilizar TypeORM, PostgreSQL, MongoDB, Jest y GitHub Actions.

Esta alternativa permitía cumplir con la separación de responsabilidades solicitada por el curso y ofrecía una arquitectura estructurada. Sin embargo, se decidió no utilizarla porque el equipo cuenta con mayor experiencia y comodidad trabajando con Python para el desarrollo backend. Utilizar Django REST Framework permite reducir la curva de aprendizaje y aprovechar conocimientos previos del equipo.

Python y Django REST Framework

Esta fue la alternativa seleccionada. El equipo posee experiencia previa utilizando Python y considera que Django REST Framework permite implementar los requisitos técnicos del curso manteniendo una estructura organizada, persistencia relacional, APIs REST, pruebas automatizadas e integración continua.

La elección no elimina la necesidad de diseñar correctamente la arquitectura. Debido a que Django permite diferentes formas de organizar la lógica de una aplicación, el equipo deberá establecer y respetar explícitamente la separación entre presentación, lógica de negocio y acceso a datos durante el desarrollo.

Consecuencias

Positivas

Se reduce la curva de aprendizaje inicial al utilizar Python, tecnología con la que el equipo posee experiencia previa.

Se puede dedicar mayor tiempo al desarrollo del dominio, reglas de negocio, arquitectura y demás objetivos del curso.

Django REST Framework facilita la construcción de una API REST sobre el ecosistema de Django.

Django ORM proporciona una capa integrada para trabajar con PostgreSQL.

El stack permite incorporar pruebas automatizadas e integración continua con las herramientas previstas para el proyecto.

El equipo puede mantener una arquitectura por capas equivalente a la solicitada, aunque la implementación concreta sea diferente a la del stack de referencia.

Negativas

Los ejemplos y demostraciones del profesor basados en Spring Boot no podrán trasladarse directamente al proyecto.

El equipo deberá adaptar conceptos y requisitos explicados utilizando Java/Spring al funcionamiento de Django y Django REST Framework.

Django no obliga por defecto a utilizar exactamente la separación por capas solicitada, por lo que el equipo deberá definirla y mantenerla de manera disciplinada.

Algunos problemas específicos del stack elegido deberán ser investigados y resueltos por el equipo sin depender directamente de los ejemplos del curso.

El uso de un stack alternativo implica responsabilidad adicional para demostrar que se cumplen los mismos objetivos y requisitos técnicos establecidos en los laboratorios.

Neutras

Los comandos de instalación, ejecución, pruebas y construcción serán diferentes a los utilizados por el stack de referencia.

La estructura de carpetas y módulos seguirá las convenciones de Python y Django en lugar de las convenciones de Java y Spring Boot.

La documentación técnica del repositorio deberá indicar claramente cómo configurar y ejecutar el proyecto con Python y Django REST Framework.

Las futuras instrucciones de los laboratorios deberán interpretarse según su objetivo técnico y adaptarse al stack seleccionado cuando hagan referencia específica a tecnologías del stack de referencia.