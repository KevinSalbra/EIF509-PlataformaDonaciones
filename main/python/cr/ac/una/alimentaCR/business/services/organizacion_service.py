from django.utils import timezone

from ...data.models import Organizacion
from ...data.repositories import OrganizacionRepository
from ..exceptions import CedulaJuridicaDuplicadaError,OrganizacionNoExisteError

class OrganizacionService:
    """
    Operaciones de negocio sobre Organizacion: consultar, registrar
    y actualizar.
    """

    def __init__(
        self,
        organizacion_repository: OrganizacionRepository = None,
    ):
        self.organizacion_repository = (
            organizacion_repository or OrganizacionRepository()
        )

    def listar(self, orden=None):
        return self.organizacion_repository.obtener_todos().order_by(
            *(orden or ["id_organizacion"]), "pk"
        )

    def obtener(self, id_organizacion: int) -> Organizacion:
        organizacion = self.organizacion_repository.obtener_por_id(
            id_organizacion
        )

        if organizacion is None:
            raise OrganizacionNoExisteError(
                f"No existe una organizacion con id {id_organizacion}."
            )

        return organizacion

    def crear(
    self,
    nombre: str,
    tipo: str,
    cedula_juridica: str,
    direccion: str,
    telefono: str,
    descripcion: str = None,
    ) -> Organizacion:
        if (
        self.organizacion_repository.obtener_por_cedula_juridica(
            cedula_juridica
        )
        is not None
        ):
            raise CedulaJuridicaDuplicadaError(
            "Ya existe una organizacion registrada con la "
            f"cedula juridica {cedula_juridica}."
        )

        organizacion = Organizacion(
        nombre=nombre,
        tipo=tipo,
        cedula_juridica=cedula_juridica,
        descripcion=descripcion,
        direccion=direccion,
        telefono=telefono,
        estado=Organizacion.Estado.PENDIENTE,
        fecha_registro=timezone.now(),
    )

        return self.organizacion_repository.guardar(organizacion)

    def actualizar(
        self,
        id_organizacion: int,
        nombre: str,
        tipo: str,
        direccion: str,
        telefono: str,
        estado: str,
        descripcion: str = None,
    ) -> Organizacion:
        organizacion = self.obtener(id_organizacion)

        organizacion.nombre = nombre
        organizacion.tipo = tipo
        organizacion.descripcion = descripcion
        organizacion.direccion = direccion
        organizacion.telefono = telefono
        organizacion.estado = estado

        return self.organizacion_repository.guardar(organizacion)