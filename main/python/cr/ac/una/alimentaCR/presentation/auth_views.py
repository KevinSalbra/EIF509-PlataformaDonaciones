from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import AuthService, UsuarioService

from .usuario_serializers import LoginRequestSerializer


class LoginView(APIView):

    @extend_schema(
        operation_id="iniciar_sesion",
        summary="Iniciar sesion",
        description=(
            "Autentica un usuario mediante correo y contrasena "
            "y retorna un token JWT."
        ),
        request=LoginRequestSerializer,
        responses={
            200: inline_serializer(
                name="LoginResponse",
                fields={
                    "access_token": serializers.CharField(),
                    "token_type": serializers.CharField(),
                },
            ),
        },
        auth=[],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = UsuarioService().autenticar(
            correo=serializer.validated_data["correo"],
            contrasena=serializer.validated_data["contrasena"],
        )

        if usuario is None:
            raise AuthenticationFailed(
                "Credenciales invalidas."
            )

        token = AuthService.generar_token(usuario)

        return Response(
            {
                "access_token": token,
                "token_type": "Bearer",
            },
            status=status.HTTP_200_OK,
        )