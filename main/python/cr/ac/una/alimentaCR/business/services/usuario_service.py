from django.contrib.auth.hashers import make_password
from django.utils import timezone

from ...data.models import Organizacion, Usuario
from ...data.repositories import OrganizacionRepository, UsuarioRepository
from ..exceptions import (
    CorreoDuplicadoError,
    OrganizacionNoExisteError,
    RolOrganizacionIncompatibleError,
    UsuarioNoExisteError,
)

# Tipo de organizacion que exige cada rol. El Administrador puede
# pertenecer a cualquier organizacion, por eso no aparece aqui.
TIPO_ORGANIZACION_POR_ROL = {
    Usuario.Rol.REPRESENTANTE_DONANTE: Organizacion.Tipo.DONANTE,
    Usuario.Rol.REPRESENTANTE_BENEFICIARIA: Organizacion.Tipo.BENEFICIARIA,
}


class UsuarioService:
    """
    Operaciones de negocio sobre Usuario: consultar, registrar y
    actualizar.

    Reglas:
    1. La Organizacion del usuario debe existir.
    2. El correo no puede estar registrado por otro usuario.
    3. El rol debe corresponder al tipo de la Organizacion (un
       representante donante pertenece a una organizacion DONANTE y un
       representante beneficiario a una BENEFICIARIA).
    4. La contrasena se guarda siempre como hash, nunca en texto plano.
    5. Todo usuario nuevo inicia en estado ACTIVO.
    """

    def __init__(
        self,
        usuario_repository: UsuarioRepository = None,
        organizacion_repository: OrganizacionRepository = None,
    ):
        self.usuario_repository = usuario_repository or UsuarioRepository()
        self.organizacion_repository = (
            organizacion_repository or OrganizacionRepository()
        )

    def listar(self):
        return list(
            self.usuario_repository.obtener_todos().order_by("id_usuario")
        )

    def obtener(self, id_usuario: int) -> Usuario:
        usuario = self.usuario_repository.obtener_por_id(id_usuario)
        if usuario is None:
            raise UsuarioNoExisteError(
                f"No existe un usuario con id {id_usuario}."
            )
        return usuario

    def crear(
        self,
        id_organizacion: int,
        nombre: str,
        correo: str,
        contrasena: str,
        rol: str,
        telefono: str = None,
    ) -> Usuario:
        organizacion = self.organizacion_repository.obtener_por_id(
            id_organizacion
        )
        if organizacion is None:
            raise OrganizacionNoExisteError(
                f"No existe una organizacion con id {id_organizacion}."
            )

        if self.usuario_repository.obtener_por_correo(correo) is not None:
            raise CorreoDuplicadoError(
                f"Ya existe un usuario registrado con el correo {correo}."
            )

        self._validar_rol_con_organizacion(rol, organizacion)

        usuario = Usuario(
            organizacion=organizacion,
            nombre=nombre,
            correo=correo,
            contrasena=make_password(contrasena),
            telefono=telefono,
            rol=rol,
            estado=Usuario.Estado.ACTIVO,
            fecha_registro=timezone.now(),
        )
        return self.usuario_repository.guardar(usuario)

    def actualizar(
        self,
        id_usuario: int,
        nombre: str,
        rol: str,
        estado: str,
        telefono: str = None,
    ) -> Usuario:
        usuario = self.obtener(id_usuario)
        self._validar_rol_con_organizacion(rol, usuario.organizacion)

        usuario.nombre = nombre
        usuario.telefono = telefono
        usuario.rol = rol
        usuario.estado = estado
        return self.usuario_repository.guardar(usuario)

    def _validar_rol_con_organizacion(
        self, rol: str, organizacion: Organizacion
    ) -> None:
        tipo_requerido = TIPO_ORGANIZACION_POR_ROL.get(rol)
        if tipo_requerido is not None and organizacion.tipo != tipo_requerido:
            raise RolOrganizacionIncompatibleError(
                f"El rol {rol} requiere una organizacion de tipo "
                f"{tipo_requerido}, pero la organizacion "
                f"{organizacion.id_organizacion} es de tipo "
                f"{organizacion.tipo}."
            )