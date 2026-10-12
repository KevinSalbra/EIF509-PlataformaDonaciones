from django.db import transaction
from django.utils import timezone

from ..dto import EntregaDTO, SolicitudDTO
from ...data.models import Donacion, Entrega, Organizacion, Solicitud
from ...data.repositories import (
    BitacoraRepository,
    DonacionRepository,
    EntregaRepository,
    SolicitudRepository,
    UsuarioRepository,
)
from ..exceptions import (
    DonacionNoDisponibleError,
    DonacionNoExisteError,
    OrganizacionNoAutorizadaError,
    SolicitudDuplicadaError,
    SolicitudNoExisteError,
    UsuarioNoAutorizadoError,
    UsuarioNoExisteError,
)
from ..specifications import (
    SolicitudDeDonacionSpecification,
    SolicitudDeOrganizacionSpecification,
    SolicitudPorEstadoSpecification,
    combinar,
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

    def aceptar_solicitud(self, id_solicitud: int, id_usuario: int) -> EntregaDTO:
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

        Devuelve un DTO inmutable para evitar exponer directamente
        la entidad ORM Entrega a la capa de presentacion.
        """
        entrega = self._aceptar_solicitud_transaccional(id_solicitud, id_usuario)
        self._registrar_evento_bitacora(entrega, id_usuario)
        return self._convertir_entrega_a_dto(entrega)
    
    def _convertir_entrega_a_dto(
        self, entrega: Entrega
    ) -> EntregaDTO:
        """
        Convierte la entidad ORM Entrega en un DTO inmutable.
        """
        return EntregaDTO(
            id_entrega=entrega.id_entrega,
            solicitud_id=entrega.solicitud_id,
            fecha_creacion=entrega.fecha_creacion,
            confirmacion_donante=entrega.confirmacion_donante,
            confirmacion_beneficiario=entrega.confirmacion_beneficiario,
            estado=entrega.estado,
        )
    
    def _convertir_solicitud_a_dto(
        self, solicitud: Solicitud
    ) -> SolicitudDTO:
        """
        Convierte la entidad ORM Solicitud en un DTO inmutable.
        """
        return SolicitudDTO(
            id_solicitud=solicitud.id_solicitud,
            donacion_id=solicitud.donacion_id,
            organizacion_beneficiaria_id=solicitud.organizacion_beneficiaria_id,
            fecha_solicitud=solicitud.fecha_solicitud,
            estado=solicitud.estado,
            observacion=solicitud.observacion,
        )

    @transaction.atomic 
    def _aceptar_solicitud_transaccional(
        self, id_solicitud: int, id_usuario: int
    ) -> Entrega:

        # 1. Identificar la solicitud y su donacion.
        solicitud_inicial = self.solicitud_repository.obtener_por_id(
            id_solicitud
        )

        if solicitud_inicial is None:
            raise SolicitudNoExisteError(
                f"No existe una solicitud con id {id_solicitud}."
            )

        # 2. Bloquear la donacion antes de validar estados.
        donacion = self.donacion_repository.obtener_por_id_para_actualizar(
            solicitud_inicial.donacion_id
        )

        if donacion is None:
            raise DonacionNoExisteError(
                f"No existe una donacion con id "
                f"{solicitud_inicial.donacion_id}."
            )

        # 3. Volver a consultar la solicitud despues del bloqueo.
        # Esto evita utilizar un estado leido antes de esperar.
        solicitud = self.solicitud_repository.obtener_por_id(
            id_solicitud
        )

        if solicitud is None:
            raise SolicitudNoExisteError(
                f"No existe una solicitud con id {id_solicitud}."
            )

        # 4. Validar las reglas de negocio.
        obtener_estado(solicitud.estado).aceptar(solicitud)

        self._validar_propietario(donacion, id_usuario)

        if donacion.estado != Donacion.Estado.DISPONIBLE:
            raise DonacionNoDisponibleError(
                f"La donacion {donacion.id_donacion} no esta disponible "
                f"(estado actual: {donacion.estado})."
            )

        # Utilizar la instancia bloqueada de la donacion.
        solicitud.donacion = donacion

        # 5. Rechazar las otras solicitudes pendientes.
        self._rechazar_otras_solicitudes_pendientes(
            donacion, solicitud
        )

        # 6. Guardar la solicitud aceptada.
        self.solicitud_repository.guardar(solicitud)

        # 7. Asignar la donacion.
        donacion.estado = Donacion.Estado.ASIGNADA
        self.donacion_repository.guardar(donacion)

        # 8. Crear la entrega.
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
        
        
    # ------------------------------------------------------------------
    # Consulta, solicitud de una donacion (Proceso 3) y cancelacion de
    # una solicitud (Proceso 4)
    # ------------------------------------------------------------------

    def listar_solicitudes(
        self,
        estado=None,
        id_organizacion=None,
        id_donacion=None,
        orden=None,
        como_dto=False, 
    ):
        """
        Devuelve un QuerySet filtrado con Specifications y ordenado.
        Solo se aplican los filtros recibidos.
        """
        filtros = []
        if estado is not None:
            filtros.append(SolicitudPorEstadoSpecification(estado))
        if id_organizacion is not None:
            filtros.append(SolicitudDeOrganizacionSpecification(id_organizacion))
        if id_donacion is not None:
            filtros.append(SolicitudDeDonacionSpecification(id_donacion))

        consulta = combinar(filtros).aplicar(
            self.solicitud_repository.obtener_todos()
        )
        return consulta.order_by(*(orden or ["id_solicitud"]), "pk")
    
    def listar_solicitudes_paginadas(
        self,
        paginador,
        request,
        estado=None,
        id_organizacion=None,
        id_donacion=None,
        orden=None,
    ):
        """
        Consulta, pagina y convierte las solicitudes a DTO.
        """
        consulta = self.listar_solicitudes(
            estado=estado,
            id_organizacion=id_organizacion,
            id_donacion=id_donacion,
            orden=orden,
        )

        pagina = paginador.paginate_queryset(consulta, request)

        return [
            self._convertir_solicitud_a_dto(solicitud)
            for solicitud in pagina
        ]

    def _obtener_solicitud_entidad(
        self, id_solicitud: int
    ) -> Solicitud:
        """
        Obtiene la entidad ORM para operaciones internas del negocio.
        """
        solicitud = self.solicitud_repository.obtener_por_id(id_solicitud)

        if solicitud is None:
            raise SolicitudNoExisteError(
                f"No existe una solicitud con id {id_solicitud}."
            )

        return solicitud

    def obtener_solicitud(
        self, id_solicitud: int
    ) -> SolicitudDTO:
        """
        Obtiene una solicitud y devuelve un DTO inmutable.
        """
        solicitud = self._obtener_solicitud_entidad(id_solicitud)
        return self._convertir_solicitud_a_dto(solicitud)

    def crear_solicitud(
        self, id_donacion: int, id_usuario: int, observacion: str = None
    ) -> SolicitudDTO:
        """
        Proceso 3: una organizacion beneficiaria solicita una donacion.

        Reglas, en orden:
        1. El usuario y la donacion deben existir.
        2. La organizacion del usuario debe ser BENEFICIARIA y estar
           APROBADA.
        3. La organizacion no puede solicitar su propia donacion.
        4. La donacion debe estar DISPONIBLE.
        5. La organizacion no puede tener otra solicitud PENDIENTE
           para la misma donacion.
        La solicitud se crea en estado PENDIENTE.
        """
        usuario = self._obtener_usuario(id_usuario)
        donacion = self.donacion_repository.obtener_por_id(id_donacion)
        if donacion is None:
            raise DonacionNoExisteError(
                f"No existe una donacion con id {id_donacion}."
            )

        organizacion = usuario.organizacion
        if (
            organizacion.tipo != Organizacion.Tipo.BENEFICIARIA
            or organizacion.estado != Organizacion.Estado.APROBADA
        ):
            raise OrganizacionNoAutorizadaError(
                f"La organizacion {organizacion.id_organizacion} debe ser "
                f"beneficiaria y estar aprobada para solicitar donaciones."
            )

        if donacion.organizacion_donante_id == organizacion.id_organizacion:
            raise OrganizacionNoAutorizadaError(
                "Una organizacion no puede solicitar su propia donacion."
            )

        if donacion.estado != Donacion.Estado.DISPONIBLE:
            raise DonacionNoDisponibleError(
                f"La donacion {id_donacion} no esta disponible "
                f"(estado actual: {donacion.estado})."
            )

        if self.solicitud_repository.existe_solicitud_pendiente(
            id_donacion, organizacion.id_organizacion
        ):
            raise SolicitudDuplicadaError(
                f"La organizacion {organizacion.id_organizacion} ya tiene "
                f"una solicitud pendiente para la donacion {id_donacion}."
            )

        solicitud = Solicitud(
            donacion=donacion,
            organizacion_beneficiaria=organizacion,
            fecha_solicitud=timezone.now(),
            estado=Solicitud.Estado.PENDIENTE,
            observacion=observacion,
        )
        solicitud_guardada = self.solicitud_repository.guardar(solicitud)
        return self._convertir_solicitud_a_dto(solicitud_guardada)

    def cancelar_solicitud(self, id_solicitud: int, id_usuario: int) -> SolicitudDTO:
        """
        Proceso 4: cancelar una solicitud pendiente.

        Reglas, en orden:
        1. La solicitud y el usuario deben existir.
        2. Solo la organizacion que creo la solicitud puede cancelarla.
        3. Solo se cancelan solicitudes PENDIENTES (lo valida el
           patron State).
        """
        solicitud = self._obtener_solicitud_entidad(id_solicitud)
        usuario = self._obtener_usuario(id_usuario)

        if usuario.organizacion_id != solicitud.organizacion_beneficiaria_id:
            raise UsuarioNoAutorizadoError(
                f"El usuario {id_usuario} no pertenece a la organizacion "
                f"que creo la solicitud {id_solicitud}."
            )

        obtener_estado(solicitud.estado).cancelar(solicitud)
        solicitud_guardada = self.solicitud_repository.guardar(solicitud)
        return self._convertir_solicitud_a_dto(solicitud_guardada)

    def _obtener_usuario(self, id_usuario: int):
        usuario = self.usuario_repository.obtener_por_id(id_usuario)
        if usuario is None:
            raise UsuarioNoExisteError(
                f"No existe un usuario con id {id_usuario}."
            )
        return usuario