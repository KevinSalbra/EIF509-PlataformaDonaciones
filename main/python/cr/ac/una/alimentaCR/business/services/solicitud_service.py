from django.db import transaction
from django.utils import timezone

from ...data.models import Donacion, Entrega
from ...data.repositories import (
    BitacoraRepository,
    DonacionRepository,
    EntregaRepository,
    SolicitudRepository,
    UsuarioRepository,
)
from ..exceptions import (
    DonacionNoDisponibleError,
    SolicitudNoExisteError,
    UsuarioNoAutorizadoError,
)
from ..states import obtener_estado


class SolicitudService:
    """
    Proceso de negocio #1: aceptar una Solicitud y generar la Entrega
    correspondiente.

    Reglas aplicadas, en orden (segun la Propuesta de Dominio, Proceso 2):
    1. La Solicitud debe existir.
    2. La Solicitud debe estar en estado PENDIENTE.
    3. El Usuario que acepta debe pertenecer a la Organizacion donante
       propietaria de la Donacion (solo el donante propietario puede
       aceptar una solicitud).
    4. La Donacion asociada debe estar en estado DISPONIBLE.
    5. Las demas Solicitudes PENDIENTES de la misma Donacion se
       rechazan (no puede haber dos Solicitudes ACEPTADAS para la
       misma Donacion).
    6. La Donacion pasa a ASIGNADA.
    7. Se crea la Entrega asociada a la Solicitud aceptada.
    8. Se registra el evento en la Bitacora (MongoDB).

    Los repositorios se reciben por parametro (con un valor por
    defecto) para poder sustituirlos por dobles de prueba (mocks) en
    las pruebas unitarias de la Meta 4, sin tocar la base de datos.
    """

    def __init__(
        self,
        solicitud_repository: SolicitudRepository = None,
        donacion_repository: DonacionRepository = None,
        entrega_repository: EntregaRepository = None,
        usuario_repository: UsuarioRepository = None,
        bitacora_repository: BitacoraRepository = None,
    ):
        self.solicitud_repository = solicitud_repository or SolicitudRepository()
        self.donacion_repository = donacion_repository or DonacionRepository()
        self.entrega_repository = entrega_repository or EntregaRepository()
        self.usuario_repository = usuario_repository or UsuarioRepository()
        self.bitacora_repository = bitacora_repository or BitacoraRepository()

    def aceptar_solicitud(self, id_solicitud: int, id_usuario: int) -> Entrega:
        """
        Punto de entrada publico del proceso.

        La parte relacional (Postgres) se ejecuta de forma atomica en
        `_aceptar_solicitud_transaccional`. El registro en la Bitacora
        (MongoDB) se hace despues, fuera de esa transaccion: Postgres
        y MongoDB son bases de datos distintas y no comparten una
        transaccion global (no hay two-phase commit entre ambas), asi
        que si el registro en Mongo llegara a fallar, los cambios de
        negocio ya confirmados en Postgres no se revierten. Esta es
        una decision de diseno explicita de persistencia poliglota
        (ver ADR-002), no un descuido.
        """
        entrega = self._aceptar_solicitud_transaccional(id_solicitud, id_usuario)
        self._registrar_evento_bitacora(entrega, id_usuario)
        return entrega

    @transaction.atomic
    def _aceptar_solicitud_transaccional(
        self, id_solicitud: int, id_usuario: int
    ) -> Entrega:
        solicitud = self.solicitud_repository.obtener_por_id(id_solicitud)
        if solicitud is None:
            raise SolicitudNoExisteError(
                f"No existe una solicitud con id {id_solicitud}."
            )

        estado_actual = obtener_estado(solicitud.estado)
        estado_actual.aceptar(solicitud)

        donacion = solicitud.donacion
        self._validar_propietario(donacion, id_usuario)

        if donacion.estado != Donacion.Estado.DISPONIBLE:
            raise DonacionNoDisponibleError(
                f"La donacion {donacion.id_donacion} no esta disponible "
                f"(estado actual: {donacion.estado})."
            )

        self._rechazar_otras_solicitudes_pendientes(donacion, solicitud)

        self.solicitud_repository.guardar(solicitud)

        donacion.estado = Donacion.Estado.ASIGNADA
        self.donacion_repository.guardar(donacion)

        entrega = Entrega(
            solicitud=solicitud,
            fecha_creacion=timezone.now(),
            confirmacion_donante=False,
            confirmacion_beneficiario=False,
            estado=Entrega.Estado.PENDIENTE,
        )
        return self.entrega_repository.guardar(entrega)

    def _validar_propietario(self, donacion: Donacion, id_usuario: int) -> None:
        usuario = self.usuario_repository.obtener_por_id(id_usuario)
        if usuario is None or usuario.organizacion_id != donacion.organizacion_donante_id:
            raise UsuarioNoAutorizadoError(
                f"El usuario {id_usuario} no pertenece a la organizacion "
                f"donante de la donacion {donacion.id_donacion}."
            )

    def _registrar_evento_bitacora(self, entrega: Entrega, id_usuario: int) -> None:
        solicitud = entrega.solicitud
        self.bitacora_repository.registrar({
            "usuario_id": id_usuario,
            "tipo_evento": "SOLICITUD_ACEPTADA",
            "entidad": "SOLICITUD",
            "entidad_id": solicitud.id_solicitud,
            "fecha_hora": timezone.now(),
            "descripcion": (
                f"Solicitud {solicitud.id_solicitud} aceptada; "
                f"donacion {solicitud.donacion_id} asignada; "
                f"entrega {entrega.id_entrega} creada."
            ),
            "datos_adicionales": {
                "id_donacion": solicitud.donacion_id,
                "id_entrega": entrega.id_entrega,
            },
        })

    def _rechazar_otras_solicitudes_pendientes(self, donacion, solicitud_aceptada):
        pendientes = self.solicitud_repository.obtener_pendientes_por_donacion(
            donacion.id_donacion
        )
        for otra_solicitud in pendientes:
            if otra_solicitud.id_solicitud == solicitud_aceptada.id_solicitud:
                continue
            obtener_estado(otra_solicitud.estado).rechazar(otra_solicitud)
            self.solicitud_repository.guardar(otra_solicitud)