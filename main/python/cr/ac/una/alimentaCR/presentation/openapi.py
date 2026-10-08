from drf_spectacular.extensions import OpenApiAuthenticationExtension


class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Define la autenticacion JWT personalizada para OpenAPI/Swagger.
    """

    target_class = (
        "cr.ac.una.alimentaCR.presentation."
        "jwt_autenticacion.JWTAuthentication"
    )

    name = "BearerAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }