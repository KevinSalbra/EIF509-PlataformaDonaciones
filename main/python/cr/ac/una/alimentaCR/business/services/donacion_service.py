from django.utils import timezone

from ...data.models import Donacion
from ...data.repositories import (
    BitacoraRepository,
    CategoriaRepository,
    DonacionRepository,
    OrganizacionRepository,
)
from ..exceptions import (
    CategoriaNoExisteError,
    OrganizacionNoExisteError,
)
from ..specifications import (
    CantidadPositivaSpecification,
    CategoriaActivaSpecification,
    FechaLimiteFuturaSpecification,
    OrganizacionPuedeDonarSpecification,
)


class DonacionService:
    """
    Proceso de negocio #2 del Laboratorio 4:
    publicar una Donacion.

    Reglas del dominio:
    1. La Organizacion debe existir.
    2. La Organizacion debe ser de tipo DONANTE.
    3. La Organizacion debe estar APROBADA.
    4. La Categoria debe existir y estar ACTIVA.
    5. La cantidad debe ser mayor que cero.
    6. La fecha limite de retiro debe ser posterior a la fecha actual.
    7. Toda nueva Donacion inicia en estado DISPONIBLE.
    8. Se registra el evento en la Bitacora.

    Se utiliza el patron Specification para encapsular las reglas
    independientes que determinan si una Donacion puede publicarse.
    """

    def __init__(
        self,
        organizacion_repository: OrganizacionRepository = None,
        categoria_repository: CategoriaRepository = None,
        donacion_repository: DonacionRepository = None,
        bitacora_repository: BitacoraRepository = None,
    ):
        self.organizacion_repository = (
            organizacion_repository or OrganizacionRepository()
        )
        self.categoria_repository = (
            categoria_repository or CategoriaRepository()
        )
        self.donacion_repository = (
            donacion_repository or DonacionRepository()
        )
        self.bitacora_repository = (
            bitacora_repository or BitacoraRepository()
        )

    def publicar_donacion(
        self,
        id_organizacion: int,
        id_categoria: int,
        alimento: str,
        descripcion: str,
        cantidad,
        unidad_medida: str,
        fecha_limite_retiro,
    ) -> Donacion:
        """
        Publica una nueva Donacion despues de validar las reglas
        de negocio definidas para este proceso.
        """

        # ---------------------------------------------------------
        # 1. Obtener y validar existencia de la Organizacion
        # ---------------------------------------------------------

        organizacion = self.organizacion_repository.obtener_por_id(
            id_organizacion
        )

        if organizacion is None:
            raise OrganizacionNoExisteError(
                f"No existe una organizacion con id {id_organizacion}."
            )

        # ---------------------------------------------------------
        # 2. Obtener y validar existencia de la Categoria
        # ---------------------------------------------------------

        categoria = self.categoria_repository.obtener_por_id(
            id_categoria
        )

        if categoria is None:
            raise CategoriaNoExisteError(
                f"No existe una categoria con id {id_categoria}."
            )

        # ---------------------------------------------------------
        # 3. Validar reglas de negocio mediante Specification
        # ---------------------------------------------------------

        especificaciones = [
            OrganizacionPuedeDonarSpecification(organizacion),
            CategoriaActivaSpecification(categoria),
            CantidadPositivaSpecification(cantidad),
            FechaLimiteFuturaSpecification(fecha_limite_retiro),
        ]

        for especificacion in especificaciones:
            especificacion.validar()

        # ---------------------------------------------------------
        # 4. Crear la Donacion
        # ---------------------------------------------------------

        donacion = Donacion(
            organizacion_donante=organizacion,
            categoria=categoria,
            alimento=alimento,
            descripcion=descripcion,
            cantidad=cantidad,
            unidad_medida=unidad_medida,
            fecha_publicacion=timezone.now(),
            fecha_limite_retiro=fecha_limite_retiro,
            estado=Donacion.Estado.DISPONIBLE,
        )

        donacion = self.donacion_repository.guardar(donacion)

        # ---------------------------------------------------------
        # 5. Registrar el evento en la Bitacora
        # ---------------------------------------------------------

        self._registrar_evento_bitacora(donacion)

        return donacion

    def _registrar_evento_bitacora(
        self,
        donacion: Donacion,
    ) -> None:
        self.bitacora_repository.registrar({
            "tipo_evento": "DONACION_PUBLICADA",
            "entidad": "DONACION",
            "entidad_id": donacion.id_donacion,
            "fecha_hora": timezone.now(),
            "descripcion": (
                f"Donacion {donacion.id_donacion} publicada "
                f"por la organizacion "
                f"{donacion.organizacion_donante_id}."
            ),
            "datos_adicionales": {
                "id_categoria": donacion.categoria_id,
                "alimento": donacion.alimento,
                "cantidad": str(donacion.cantidad),
                "unidad_medida": donacion.unidad_medida,
            },
        })