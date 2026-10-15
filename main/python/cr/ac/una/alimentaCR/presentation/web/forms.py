"""
Formularios del modulo administrativo.

Equivalen a los objetos de formulario + BindingResult de Spring MVC:
validan el formato de los campos y acumulan los errores por campo.
Las reglas de negocio (duplicados, etc.) las decide la capa de
negocio; sus excepciones se convierten en errores del formulario
desde las vistas.
"""
from django import forms

from cr.ac.una.alimentaCR.data.models import Categoria, Organizacion

MENSAJES = {
    "required": "Este campo es obligatorio.",
}

REGEX_CEDULA = r"^\d-\d{3}-\d{6}$"
REGEX_TELEFONO = r"^\d{4}-\d{4}$"


class LoginForm(forms.Form):
    correo = forms.EmailField(
        label="Correo",
        max_length=150,
        error_messages={**MENSAJES, "invalid": "Ingrese un correo válido."},
    )
    contrasena = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        error_messages=MENSAJES,
    )


class CategoriaForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        max_length=100,
        error_messages={
            **MENSAJES,
            "max_length": "Máximo 100 caracteres.",
        },
    )
    descripcion = forms.CharField(
        label="Descripción",
        max_length=250,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        error_messages={"max_length": "Máximo 250 caracteres."},
    )
    estado = forms.ChoiceField(
        label="Estado",
        choices=Categoria.Estado.choices,
        error_messages={
            **MENSAJES,
            "invalid_choice": "Seleccione un estado válido.",
        },
    )

    def __init__(self, *args, con_estado=False, **kwargs):
        super().__init__(*args, **kwargs)
        # Al crear, el servicio fija el estado inicial (ACTIVA).
        if not con_estado:
            del self.fields["estado"]

    def clean_descripcion(self):
        return self.cleaned_data["descripcion"].strip() or None


class OrganizacionForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        max_length=150,
        error_messages={
            **MENSAJES,
            "max_length": "Máximo 150 caracteres.",
        },
    )
    tipo = forms.ChoiceField(
        label="Tipo",
        choices=Organizacion.Tipo.choices,
        error_messages={
            **MENSAJES,
            "invalid_choice": "Seleccione un tipo válido.",
        },
    )
    cedula_juridica = forms.RegexField(
        label="Cédula jurídica",
        regex=REGEX_CEDULA,
        max_length=30,
        help_text="Formato: 3-101-123456",
        error_messages={
            **MENSAJES,
            "invalid": "Use el formato 3-101-123456.",
        },
    )
    direccion = forms.CharField(
        label="Dirección",
        max_length=250,
        error_messages={
            **MENSAJES,
            "max_length": "Máximo 250 caracteres.",
        },
    )
    telefono = forms.RegexField(
        label="Teléfono",
        regex=REGEX_TELEFONO,
        max_length=20,
        help_text="Ejemplo: 2200-0001",
        error_messages={
            **MENSAJES,
            "invalid": "Use el formato 2200-0001.",
        },
    )
    descripcion = forms.CharField(
        label="Descripción",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        error_messages={"max_length": "Máximo 500 caracteres."},
    )
    estado = forms.ChoiceField(
        label="Estado",
        choices=Organizacion.Estado.choices,
        error_messages={
            **MENSAJES,
            "invalid_choice": "Seleccione un estado válido.",
        },
    )

    def __init__(self, *args, edicion=False, **kwargs):
        super().__init__(*args, **kwargs)
        if edicion:
            # La cedula juridica identifica a la organizacion y el
            # servicio de actualizacion no la modifica.
            del self.fields["cedula_juridica"]
        else:
            # Al crear, el servicio fija el estado inicial (PENDIENTE).
            del self.fields["estado"]

    def clean_descripcion(self):
        return self.cleaned_data["descripcion"].strip() or None