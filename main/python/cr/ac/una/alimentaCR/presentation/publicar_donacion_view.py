from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cr.ac.una.alimentaCR.business.exceptions import (
    CantidadInvalidaError,
    CategoriaInactivaError,
    CategoriaNoExisteError,
    FechaLimiteInvalidaError,
    OrganizacionNoAutorizadaError,
    OrganizacionNoExisteError,
)
from cr.ac.una.alimentaCR.business.services import DonacionService

from .serializers import (
    DonacionResponseSerializer,
    PublicarDonacionRequestSerializer,
)


class PublicarDonacionView(APIView):
    """
    Expone el Proceso #2 (publicar una Donacion) como endpoint REST.

    La vista valida el formato de entrada mediante el DTO, invoca al
    servicio de negocio, traduce las excepciones de negocio a codigos
    HTTP y serializa la Donacion creada mediante el DTO de salida.

    Ninguna regla de negocio se implementa en esta vista.
    """

    def post(self, request):
        request_serializer = PublicarDonacionRequestSerializer(
            data=request.data
        )
        request_serializer.is_valid(raise_exception=True)

        datos = request_serializer.validated_data

        try:
            donacion = DonacionService().publicar_donacion(
                id_organizacion=datos["id_organizacion"],
                id_categoria=datos["id_categoria"],
                alimento=datos["alimento"],
                descripcion=datos.get("descripcion"),
                cantidad=datos["cantidad"],
                unidad_medida=datos["unidad_medida"],
                fecha_limite_retiro=datos["fecha_limite_retiro"],
            )

        except (
            OrganizacionNoExisteError,
            CategoriaNoExisteError,
        ) as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except OrganizacionNoAutorizadaError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_403_FORBIDDEN,
            )

        except (
            CategoriaInactivaError,
            CantidadInvalidaError,
            FechaLimiteInvalidaError,
        ) as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = DonacionResponseSerializer(donacion)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )