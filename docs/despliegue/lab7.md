# Laboratorio 7: configuración manual del pipeline y de Render

Lo que no se puede dejar en el código y debe configurarse una vez.

## 1. Deploy hook de Render → secreto de GitHub

1. Render → servicio de la API → **Settings → Deploy Hook**: copie la URL.
2. GitHub → **Settings → Secrets and variables → Actions → New repository secret**:
   nombre `DEPLOY_HOOK_API`, valor la URL. (Si la SPA también se despliega por hook,
   cree `DEPLOY_HOOK_SPA`.)
3. **Nunca** pegue la URL en un archivo, en el README ni en `AUDITORIA-SEGURIDAD.md`.

## 2. Desactivar el despliegue automático por push en Render

Render → servicio → **Settings → Build & Deploy → Auto-Deploy → No** (API y SPA).
Así solo se despliega lo que pasó por el pipeline.

## 3. Health check en Render

Render → servicio de la API → **Settings → Health Check Path**: `/actuator/health`.

## 4. Protección de la rama `main`

GitHub → **Settings → Branches → Add branch ruleset / protection rule** para `main`:

- Require a pull request before merging.
- Require status checks to pass: seleccione **`verificar`**.
- Require branches to be up to date before merging.
- (Recomendado) Block force pushes.

## 5. Variables de entorno en Render (seguridad)

| Variable | Valor |
|---|---|
| `SECRET_KEY` | Cadena aleatoria de 50+ caracteres (firma las sesiones y los JWT). |
| `DEBUG` | `False` |
| `CORS_ALLOWED_ORIGINS` | Solo la URL de la SPA (sin `*`, sin barra final). |
| `CSRF_TRUSTED_ORIGINS` | Solo la URL de la API para el panel. |
| `ALLOWED_HOSTS` | El dominio de la API. |

Generar una clave: `python -c "import secrets; print(secrets.token_urlsafe(64))"`.

## 6. Dependabot

`.github/dependabot.yml` ya está en el repositorio; verifique en **Settings → Code
security** que *Dependabot alerts* esté activado.

## 7. Verificar que funciona

1. Un cambio pequeño en `main` → pipeline en verde → la API se actualiza sola.
2. Rompa una prueba a propósito en una rama/PR → `verificar` falla → `desplegar` no corre.
3. `curl https://<api>/actuator/health` → `{"status":"UP"}`.
4. En *Logs* de Render, intente un login con clave incorrecta y busque `"evento": "login_fallido"`.