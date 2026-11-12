# ADR-006 · Plataforma y estrategia de despliegue

**Responsables:** Kevin Salazar Bravo y Kimberley Gómez Quesada

## Contexto

AlimentaCR está compuesto por diferentes elementos que deben funcionar de manera integrada:

- Una SPA desarrollada con React.
- Una API REST desarrollada con Django REST Framework.
- Un panel administrativo MVC integrado en Django.
- Una base de datos relacional PostgreSQL.
- Una base de datos documental MongoDB.
- Migraciones relacionales administradas mediante Flyway.

El sistema debía quedar disponible públicamente para su evaluación sin requerir que el profesor instalara Python, Node.js, PostgreSQL, MongoDB o Flyway en su computadora.

También era necesario mantener diferencias entre desarrollo y producción sin incluir credenciales ni valores sensibles dentro del repositorio. El entorno desplegado debía utilizar HTTPS, bases de datos administradas y un proceso reproducible para construir e iniciar el backend.

El proyecto es desarrollado por un equipo de dos personas dentro de un periodo académico limitado. Por esta razón, la plataforma debía reducir las tareas de administración de servidores y permitir desplegar los componentes sin mantener infraestructura física propia.

## Decisión

Se utilizará una estrategia de despliegue basada en servicios administrados:

- Render Web Service para la API Django y el panel MVC.
- Render Static Site para la SPA React.
- Render PostgreSQL para la persistencia relacional.
- MongoDB Atlas para la bitácora documental.
- Docker para empaquetar el backend.
- Gunicorn como servidor de aplicación en producción.
- Flyway para aplicar las migraciones antes de iniciar Django.
- Variables de entorno para proporcionar la configuración de cada ambiente.

### Backend

La API REST y el panel MVC se ejecutan dentro del mismo servicio Django.

El backend se empaqueta mediante un `Dockerfile` basado en una imagen ligera de Python. La imagen contiene:

- El código de Django.
- Las dependencias de Python.
- Gunicorn.
- Flyway y los componentes necesarios para ejecutarlo.
- Las migraciones SQL.
- El script de arranque.

La imagen establece el paquete `main/python` como parte de la ruta de módulos de Python y expone el puerto utilizado por el servidor.

En producción no se utiliza `manage.py runserver`. Gunicorn carga la aplicación WSGI de Django y escucha en el puerto proporcionado por la plataforma.

### Migraciones durante el arranque

El contenedor ejecuta `scripts/start.sh` como comando de inicio.

La secuencia es:

1. Iniciar Flyway.
2. Establecer la conexión con PostgreSQL usando la configuración del entorno.
3. Validar el historial de migraciones.
4. Aplicar las migraciones pendientes.
5. Iniciar Gunicorn únicamente si Flyway finaliza correctamente.

El script utiliza una configuración que detiene la ejecución si un comando falla. Por lo tanto, una migración fallida impide que el backend inicie con un esquema incompleto o incompatible.

Flyway se mantiene como la fuente de verdad del esquema relacional.

### SPA React

La SPA se construye mediante Vite y se publica como un sitio estático independiente.

Durante el proceso de construcción se genera el directorio de distribución con los archivos HTML, CSS y JavaScript que serán servidos al navegador.

La dirección de la API se proporciona mediante una variable de configuración durante la construcción de la SPA.

Separar React del backend permite desplegar la interfaz como contenido estático y mantener independiente su ciclo de construcción.

### Bases de datos

PostgreSQL se ejecuta como un servicio administrado en Render y almacena las entidades transaccionales del dominio.

MongoDB Atlas almacena la colección documental utilizada como bitácora de eventos.

El backend se conecta con ambas bases mediante configuración suministrada por el entorno. Los valores de conexión y las credenciales no forman parte del código fuente ni de la documentación versionada.

### Configuración y secretos

La configuración de producción se administra desde las opciones de entorno proporcionadas por las plataformas.

Las categorías de configuración incluyen:

- Configuración general de Django.
- Hosts y orígenes autorizados.
- Firma de sesiones y tokens.
- Conexión con PostgreSQL.
- Conexión con MongoDB.
- Puerto de ejecución.
- Dirección pública de la API consumida por React.

Los valores sensibles se mantienen fuera del repositorio.

El archivo `.env` se utiliza únicamente para la configuración local y permanece excluido del control de versiones. El archivo `.env.example` documenta solamente los nombres de las variables requeridas, sin proporcionar valores reales de producción.

### Desarrollo local

En desarrollo se utiliza Docker Compose para ejecutar:

- PostgreSQL.
- MongoDB.
- Flyway.

El backend y la SPA también pueden ejecutarse localmente utilizando sus herramientas de desarrollo.

Esta configuración permite reproducir la infraestructura necesaria sin instalar directamente los motores de base de datos en el sistema operativo.

La configuración local y la de producción utilizan los mismos esquemas y migraciones, pero emplean conexiones y valores independientes.

## Alternativas consideradas

### Ejecutar el sistema únicamente de forma local

Esta alternativa consistía en demostrar el proyecto desde las computadoras de los integrantes utilizando Docker Compose.

No fue seleccionada como estrategia final porque el sistema no estaría permanentemente disponible para evaluación. También dependería de la conectividad, configuración y disponibilidad del equipo utilizado durante la demostración.

Docker Compose se conserva para desarrollo, pero no como plataforma de producción.

### Desplegar todos los componentes en una máquina virtual

Esta alternativa consistía en utilizar una única máquina virtual para ejecutar Django, React, PostgreSQL y MongoDB.

No fue seleccionada porque habría requerido administrar el sistema operativo, actualizaciones, certificados, procesos, puertos, respaldos y disponibilidad de las bases de datos.

Aunque ofrecería mayor control, también aumentaría la carga operativa para un equipo de dos personas.

### Ejecutar todas las tecnologías mediante contenedores en un único servicio

Esta alternativa consistía en desplegar el backend, React y ambas bases de datos dentro de una misma infraestructura de contenedores.

No fue seleccionada porque mezclaría componentes con ciclos de vida y necesidades de persistencia diferentes. También obligaría al equipo a administrar volúmenes, respaldos y disponibilidad de las bases de datos.

### Utilizar Kubernetes

Esta alternativa permitiría orquestar contenedores, escalarlos y administrar su disponibilidad mediante una plataforma especializada.

No fue seleccionada porque la complejidad de configuración y operación no se justifica para el tamaño, alcance y carga esperada del proyecto académico.

### Utilizar Render y MongoDB Atlas

Esta fue la alternativa seleccionada porque permite desplegar la aplicación y sus bases de datos mediante servicios administrados, reduciendo las tareas de infraestructura y manteniendo una separación clara entre los componentes.

## Consecuencias

### Positivas

- El sistema queda disponible mediante servicios públicos HTTPS.
- El profesor puede evaluar la aplicación sin instalar el entorno local.
- Docker proporciona un entorno consistente para ejecutar el backend.
- Gunicorn sustituye el servidor de desarrollo de Django en producción.
- Flyway aplica automáticamente las migraciones antes de iniciar la aplicación.
- Una migración fallida impide iniciar el backend con un esquema inconsistente.
- React puede publicarse como contenido estático separado del backend.
- PostgreSQL y MongoDB utilizan servicios administrados.
- Las credenciales y configuraciones sensibles permanecen fuera del repositorio.
- Docker Compose conserva un entorno local reproducible.
- La separación por componentes permite desplegar nuevamente la SPA sin reconstruir necesariamente el backend.
- La infraestructura seleccionada reduce las tareas de administración para el equipo.

### Negativas

- El sistema depende de la disponibilidad de Render y MongoDB Atlas.
- Los servicios gratuitos pueden suspenderse después de periodos de inactividad y provocar demora en la primera solicitud.
- El backend no inicia si PostgreSQL no está disponible o si Flyway no puede completar las migraciones.
- Ejecutar las migraciones durante el arranque puede aumentar el tiempo necesario para iniciar el servicio.
- Incorporar Flyway y Java dentro de la imagen aumenta su tamaño.
- La persistencia se distribuye entre dos plataformas distintas.
- El equipo debe configurar correctamente la conectividad, los orígenes permitidos y los ambientes de cada servicio.
- La configuración de Django se mantiene en un archivo compartido cuyo comportamiento depende del entorno, en lugar de utilizar módulos separados para desarrollo y producción.
- El nivel gratuito no ofrece las mismas garantías de rendimiento y disponibilidad que una infraestructura contratada.

### Neutras

- Los cambios en el esquema relacional deberán continuar realizándose mediante nuevas migraciones Flyway.
- Los cambios en React requieren una nueva construcción del sitio estático.
- Los cambios en el backend requieren construir y desplegar una nueva imagen.
- La configuración de cada ambiente debe mantenerse de manera independiente.
- Si aumenta la carga del sistema, deberá evaluarse una estrategia de escalamiento, monitoreo y respaldo más completa.
- La plataforma elegida puede sustituirse en el futuro mientras se mantengan el contenedor del backend, las migraciones y la configuración externa.