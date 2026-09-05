class BaseRepository:

    model = None

    def obtener_todos(self):
        return self.model.objects.all()

    def obtener_por_id(self, id):
        return self.model.objects.filter(pk=id).first()

    def guardar(self, entidad):
        entidad.save()
        return entidad

    def eliminar(self, entidad):
        entidad.delete()