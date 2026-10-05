from ...data.models import Categoria
from ...data.repositories import CategoriaRepository
from ..exceptions import CategoriaNoExisteError,NombreCategoriaDuplicadoError

class CategoriaService:
    """
    Operaciones de negocio sobre Categoria: consultar,
    registrar y actualizar.
    """

    def __init__(
        self,
        categoria_repository: CategoriaRepository = None,
    ):
        self.categoria_repository = (
            categoria_repository or CategoriaRepository()
        )

    def listar(self, orden=None):
        return self.categoria_repository.obtener_todos().order_by(
            *(orden or ["id_categoria"]), "pk"
        )

    def obtener(self, id_categoria: int) -> Categoria:
        categoria = self.categoria_repository.obtener_por_id(
            id_categoria
        )

        if categoria is None:
            raise CategoriaNoExisteError(
                f"No existe una categoria con id {id_categoria}."
            )

        return categoria

    def crear(
    self,
    nombre: str,
    descripcion: str = None,
    ) -> Categoria:
        if (
        self.categoria_repository.obtener_por_nombre(nombre)
        is not None
        ):
            raise NombreCategoriaDuplicadoError(
            f"Ya existe una categoria registrada con el nombre {nombre}."
        )

        categoria = Categoria(
        nombre=nombre,
        descripcion=descripcion,
        estado=Categoria.Estado.ACTIVA,
    )
        return self.categoria_repository.guardar(categoria)

    def actualizar(
    self,
    id_categoria: int,
    nombre: str,
    estado: str,
    descripcion: str = None,
    ) -> Categoria:
        categoria = self.obtener(id_categoria)

        categoria_existente = (
            self.categoria_repository.obtener_por_nombre(nombre)
    )
        if (
        categoria_existente is not None
        and categoria_existente.id_categoria
        != categoria.id_categoria
        ):
            raise NombreCategoriaDuplicadoError(
            f"Ya existe una categoria registrada con el nombre {nombre}."
        )

        categoria.nombre = nombre
        categoria.descripcion = descripcion
        categoria.estado = estado
        
        return self.categoria_repository.guardar(categoria)