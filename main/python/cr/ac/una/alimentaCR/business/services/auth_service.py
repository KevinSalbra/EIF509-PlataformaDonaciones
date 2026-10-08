from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone


class AuthService:

    @staticmethod
    def generar_token(usuario):
        ahora = timezone.now()

        payload = {
            "sub": str(usuario.id_usuario),
            "rol": usuario.rol,
            "id_organizacion": usuario.organizacion_id,
            "iat": ahora,
            "exp": ahora + timedelta(hours=1),
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )