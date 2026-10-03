from django.utils import timezone

from ...data.models import Entrega
from ...data.repositories import EntregaRepository, UsuarioRepository
from ..exceptions import (
    EntregaNoExisteError,
    EntregaNoPendienteError,
    FechaAcordadaInvalidaError,
    UsuarioNoAutorizadoError,
    UsuarioNoExisteError,
)

CAMPOS_COORDINACION = ("fecha_acordada", "lugar", "observaciones")


class EntregaService:
    """
    Consulta y coordinacion de Entregas (Proceso 5).

    Las Entregas no se crean aqui: las genera el proceso de aceptar una
    Solicitud (SolicitudService.aceptar_solicitud).

    Reglas de coordinar_entrega, en orden:
    1. La Entrega y el Usuario deben existir.
    2. Solo las organizaciones involucradas (la donante de la donacion y
       la beneficiaria de la solicitud) pueden coordinarla.
    3. La Entrega debe seguir PENDIENTE.
    4. La fecha acordada no puede ser anterior a la fecha actual.
    """

    def __init__(
        self,
        entrega_repository: EntregaRepository = None,
        usuario_repository: UsuarioRepository = None,
    ):
        self.entrega_repository = entrega_repository or EntregaRepository()
        self.usuario_repository = usuario_repository or UsuarioRepository()

    def listar_entregas(self):
        return list(
            self.entrega_repository.obtener_todos().order_by("id_entrega")
        )

    def obtener_entrega(self, id_entrega: int) -> Entrega:
        entrega = self.entrega_repository.obtener_por_id(id_entrega)
        if entrega is None:
            raise EntregaNoExisteError(
                f"No existe una entrega con id {id_entrega}."
            )
        return entrega

    def coordinar_entrega(
        self, id_entrega: int, id_usuario: int, cambios: dict
    ) -> Entrega:
        """
        Actualiza solo los campos de coordinacion presentes en `cambios`
        (fecha_acordada, lugar, observaciones).
        """
        entrega = self.obtener_entrega(id_entrega)

        usuario = self.usuario_repository.obtener_por_id(id_usuario)
        if usuario is None:
            raise UsuarioNoExisteError(
                f"No existe un usuario con id {id_usuario}."
            )

        self._validar_organizacion_involucrada(entrega, usuario)

        if entrega.estado != Entrega.Estado.PENDIENTE:
            raise EntregaNoPendienteError(
                f"La entrega {id_entrega} no esta pendiente "
                f"(estado actual: {entrega.estado})."
            )

        fecha_acordada = cambios.get("fecha_acordada")
        if fecha_acordada is not None and fecha_acordada < timezone.now():
            raise FechaAcordadaInvalidaError(
                "La fecha acordada no puede ser anterior a la fecha actual."
            )

        for campo in CAMPOS_COORDINACION:
            if campo in cambios:
                setattr(entrega, campo, cambios[campo])
        return self.entrega_repository.guardar(entrega)

    def _validar_organizacion_involucrada(self, entrega, usuario) -> None:
        solicitud = entrega.solicitud
        organizaciones_involucradas = {
            solicitud.organizacion_beneficiaria_id,
            solicitud.donacion.organizacion_donante_id,
        }
        if usuario.organizacion_id not in organizaciones_involucradas:
            raise UsuarioNoAutorizadoError(
                f"El usuario {usuario.id_usuario} no pertenece a una "
                f"organizacion involucrada en la entrega {entrega.id_entrega}."
            )