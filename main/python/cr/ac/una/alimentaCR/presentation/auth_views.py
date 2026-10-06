from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import AuthService, UsuarioService

from .usuario_serializers import LoginRequestSerializer


class LoginView(APIView):

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = UsuarioService().autenticar(
            correo=serializer.validated_data["correo"],
            contrasena=serializer.validated_data["contrasena"],
        )

        if usuario is None:
            return Response(
                {"detail": "Credenciales invalidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = AuthService.generar_token(usuario)

        return Response(
            {
                "access_token": token,
                "token_type": "Bearer",
            },
            status=status.HTTP_200_OK,
        )