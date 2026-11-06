from ..exceptions import ConflictoConcurrenciaError


class BaseRepository:

    model = None

    def obtener_todos(self):
        return self.model.objects.all()

    def obtener_por_id(self, id):
        return self.model.objects.filter(pk=id).first()

    def guardar(self, entidad):
        """
        Inserta o actualiza la entidad.

        Si la entidad ya existe y tiene un campo `version`, se aplica
        bloqueo optimista: el UPDATE solo afecta la fila si conserva la
        version leida (UPDATE ... WHERE pk = ? AND version = ?) y la
        incrementa. Si otra transaccion la modifico antes, no se
        actualiza ninguna fila y se lanza ConflictoConcurrenciaError
        (la API responde 409).
        """
        if self._usa_bloqueo_optimista(entidad):
            self._actualizar_con_version(entidad)
        else:
            entidad.save()
        return entidad

    def eliminar(self, entidad):
        entidad.delete()

    @staticmethod
    def _usa_bloqueo_optimista(entidad):
        campos = {c.name for c in entidad._meta.concrete_fields}
        return (
            "version" in campos
            and entidad.pk is not None
            and not entidad._state.adding
        )

    @staticmethod
    def _actualizar_con_version(entidad):
        modelo = type(entidad)
        version_leida = entidad.version

        valores = {
            campo.attname: getattr(entidad, campo.attname)
            for campo in modelo._meta.concrete_fields
            if not campo.primary_key and campo.name != "version"
        }

        filas = (
            modelo._default_manager
            .filter(pk=entidad.pk, version=version_leida)
            .update(version=version_leida + 1, **valores)
        )

        if filas == 0:
            raise ConflictoConcurrenciaError(
                "Otra persona modifico este registro "
                f"({modelo._meta.verbose_name} {entidad.pk}). "
                "Recargue los datos e intente de nuevo."
            )

        entidad.version = version_leida + 1