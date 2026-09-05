from ...config.mongodb import obtener_base_datos_bitacora


class BitacoraRepository:
    """
    Repositorio de la coleccion "eventos" en MongoDB.

    No hereda de BaseRepository porque esa clase asume el ORM de
    Django (self.model.objects), y la bitacora no utiliza modelos de
    Django sino el cliente de MongoDB directamente.
    """

    coleccion = "eventos"

    def _obtener_coleccion(self):
        db = obtener_base_datos_bitacora()
        return db[self.coleccion]

    def obtener_todos(self):
        return list(
            self._obtener_coleccion()
            .find()
            .sort("fecha_hora", -1)
        )

    def obtener_por_entidad(self, entidad, entidad_id):
        return list(
            self._obtener_coleccion()
            .find({
                "entidad": entidad,
                "entidad_id": entidad_id,
            })
            .sort("fecha_hora", -1)
        )

    def obtener_por_usuario(self, usuario_id):
        return list(
            self._obtener_coleccion()
            .find({"usuario_id": usuario_id})
            .sort("fecha_hora", -1)
        )

    def obtener_por_tipo_evento(self, tipo_evento):
        return list(
            self._obtener_coleccion()
            .find({"tipo_evento": tipo_evento})
            .sort("fecha_hora", -1)
        )

    def registrar(self, evento):
        resultado = self._obtener_coleccion().insert_one(evento)
        evento["_id"] = resultado.inserted_id
        return evento