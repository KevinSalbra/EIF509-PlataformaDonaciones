export default function Paginacion({ pagina, totalPaginas, total, onCambiar }) {
  if (totalPaginas <= 1) return null;
  return (
    <nav className="paginacion" aria-label="Paginación">
      <button className="btn sec" disabled={pagina <= 1} onClick={() => onCambiar(pagina - 1)}>
        Anterior
      </button>
      <span>
        Página {pagina} de {totalPaginas} · {total} registros
      </span>
      <button className="btn sec" disabled={pagina >= totalPaginas} onClick={() => onCambiar(pagina + 1)}>
        Siguiente
      </button>
    </nav>
  );
}