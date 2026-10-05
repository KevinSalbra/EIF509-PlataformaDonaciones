from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.services import UsuarioService

from .usuario_serializers import (
    ActualizarUsuarioRequestSerializer,
    CrearUsuarioRequestSerializer,
    UsuarioResponseSerializer,
)

from .listados import UsuarioConsultaSerializer, listar_paginado

class UsuarioListaView(APIView):
    """
    GET  /api/v1/usuarios  -> 200, lista de usuarios
    POST /api/v1/usuarios  -> 201 + Location | 400, 404, 409, 422
    """

    def get(self, request):
        consulta = UsuarioConsultaSerializer(data=request.query_params)
        consulta.is_valid(raise_exception=True)
        coleccion = UsuarioService().listar(orden=consulta.orden())
        return listar_paginado(request, coleccion, UsuarioResponseSerializer)

    def post(self, request):
        entrada = CrearUsuarioRequestSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        usuario = UsuarioService().crear(
            id_organizacion=datos["id_organizacion"],
            nombre=datos["nombre"],
            correo=datos["correo"],
            contrasena=datos["contrasena"],
            rol=datos["rol"],
            telefono=datos.get("telefono"),
        )

        respuesta = Response(
            UsuarioResponseSerializer(usuario).data,
            status=status.HTTP_201_CREATED,
        )
        respuesta["Location"] = request.build_absolute_uri(
            reverse("usuario_detalle", args=[usuario.id_usuario])
        )
        return respuesta


class UsuarioDetalleView(APIView):
    """
    GET /api/v1/usuarios/<id>  -> 200 | 404
    PUT /api/v1/usuarios/<id>  -> 200 | 400, 404, 422
    """

    def get(self, request, id_usuario: int):
        usuario = UsuarioService().obtener(id_usuario)
        return Response(UsuarioResponseSerializer(usuario).data)

    def put(self, request, id_usuario: int):
        entrada = ActualizarUsuarioRequestSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        usuario = UsuarioService().actualizar(
            id_usuario=id_usuario,
            nombre=datos["nombre"],
            rol=datos["rol"],
            estado=datos["estado"],
            telefono=datos.get("telefono"),
        )
        return Response(UsuarioResponseSerializer(usuario).data)