from rest_framework.permissions import BasePermission

from cr.ac.una.alimentaCR.data.models import Usuario


class EsAdministrador(BasePermission):
    """
    Permite el acceso unicamente a usuarios con rol ADMINISTRADOR.
    """

    message = "Se requiere el rol de administrador."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == Usuario.Rol.ADMINISTRADOR
        )


class EsRepresentanteDonante(BasePermission):
    """
    Permite el acceso unicamente a representantes de organizaciones
    donantes.
    """

    message = "Se requiere el rol de representante donante."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == Usuario.Rol.REPRESENTANTE_DONANTE
        )


class EsRepresentanteBeneficiaria(BasePermission):
    """
    Permite el acceso unicamente a representantes de organizaciones
    beneficiarias.
    """

    message = "Se requiere el rol de representante beneficiaria."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol
            == Usuario.Rol.REPRESENTANTE_BENEFICIARIA
        )
    
class EsRepresentanteOrganizacion(BasePermission):
    """
    Permite acceso a representantes donantes o beneficiarios.
    """

    message = (
        "Se requiere el rol de representante "
        "donante o beneficiaria."
    )

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol
            in (
                Usuario.Rol.REPRESENTANTE_DONANTE,
                Usuario.Rol.REPRESENTANTE_BENEFICIARIA,
            )
        )