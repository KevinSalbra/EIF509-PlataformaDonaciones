import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from cr.ac.una.alimentaCR.data.models import Usuario


class JWTAuthentication(BaseAuthentication):
    """
    Autenticacion stateless mediante JWT.

    Espera:
    Authorization: Bearer <token>
    """

    keyword = "Bearer"

    def authenticate(self, request):
        encabezado = request.headers.get("Authorization")

        # Si no hay token, esta clase no autentica al usuario.
        if not encabezado:
            return None

        partes = encabezado.split()

        if len(partes) != 2 or partes[0] != self.keyword:
            raise AuthenticationFailed(
                "Encabezado de autorizacion invalido."
            )

        token = partes[1]

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(
                "El token ha expirado."
            )

        except jwt.InvalidTokenError:
            raise AuthenticationFailed(
                "Token invalido."
            )

        id_usuario = payload.get("sub")

        if not id_usuario:
            raise AuthenticationFailed(
                "Token invalido."
            )

        try:
            usuario = Usuario.objects.get(
                pk=id_usuario,
                estado=Usuario.Estado.ACTIVO,
            )

        except Usuario.DoesNotExist:
            raise AuthenticationFailed(
                "Usuario no valido o inactivo."
            )

        return usuario, token

    def authenticate_header(self, request):
        return self.keyword