# ADR-005 · Estrategia de autenticación y autorización

**Responsables:** Kevin Salazar Bravo y Kimberley Gómez Quesada

## Contexto

AlimentaCR dispone de dos interfaces que necesitan autenticar usuarios:

1. Una SPA desarrollada con React que consume la API REST.
2. Un panel administrativo MVC renderizado por Django.

La API debe permitir que los usuarios se autentiquen mediante correo y contraseña y posteriormente realicen solicitudes HTTP desde una aplicación independiente. El panel administrativo, en cambio, se ejecuta dentro del mismo servicio Django y utiliza formularios y navegación renderizada en el servidor.

El sistema también debe diferenciar tres roles:

- `ADMINISTRADOR`.
- `REPRESENTANTE_DONANTE`.
- `REPRESENTANTE_BENEFICIARIA`.

Además de identificar al usuario, la estrategia debe restringir las operaciones según su rol y organización. Los representantes no deben consultar ni modificar recursos pertenecientes a otras organizaciones.

Las contraseñas, claves de firma y credenciales de infraestructura no pueden almacenarse en texto plano dentro del código fuente o del repositorio.

## Decisión

Se utilizará una estrategia de autenticación diferenciada según la interfaz:

- La API REST utilizará autenticación sin estado mediante JSON Web Tokens.
- El panel MVC utilizará una sesión firmada en cookie y protección CSRF.
- La autorización se aplicará mediante roles y alcance por organización.

### Autenticación de la API REST

El endpoint de inicio de sesión recibe correo y contraseña. `UsuarioService` consulta el usuario y verifica:

- Que el correo corresponda a un usuario existente.
- Que el usuario se encuentre en estado `ACTIVO`.
- Que la contraseña coincida con el hash almacenado.

La contraseña se comprueba mediante `check_password()` de Django. Las contraseñas nuevas se almacenan utilizando `make_password()`, por lo que no se guardan en texto plano.

Cuando las credenciales son válidas, `AuthService` genera un JWT firmado con el algoritmo `HS256` y con una vigencia de una hora.

El token contiene las siguientes declaraciones:

- `sub`: identificador del usuario.
- `rol`: rol del usuario.
- `id_organizacion`: organización a la que pertenece.
- `iat`: fecha y hora de emisión.
- `exp`: fecha y hora de expiración.

La aplicación cliente debe enviar el token en cada solicitud protegida mediante:

```http
Authorization: Bearer <token>