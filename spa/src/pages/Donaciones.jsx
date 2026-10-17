import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listarDonaciones } from "../api/client.js";
import { useAuth } from "../auth/AuthContext.jsx";
import Paginacion from "../components/Paginacion.jsx";

const ESTADOS = ["", "DISPONIBLE", "ASIGNADA", "ENTREGADA", "CANCELADA", "VENCIDA"];
const UNIDADES = {
  KILOGRAMO: "kg", GRAMO: "g", LITRO: "L", MILILITRO: "mL",
  UNIDAD: "unid.", PAQUETE: "paq.", CAJA: "caja(s)",
};

export default function Donaciones() {
  const { sesion } = useAuth();
  const [pagina, setPagina] = useState(1);
  const [estado, setEstado] = useState("");
  const [intento, setIntento] = useState(0); // para el boton "Reintentar"
  // Tres estados de la pantalla: cargando, error y datos.
  const [vista, setVista] = useState({ estado: "cargando", datos: null, error: "" });

  useEffect(() => {
    const control = new AbortController();
    setVista((previa) => ({ ...previa, estado: "cargando", error: "" }));

    listarDonaciones(
      { page: pagina, estado: estado || undefined, ordering: "-fecha_publicacion" },
      control.signal
    )
      .then((datos) => setVista({ estado: "datos", datos, error: "" }))
      .catch((e) => {
        if (e.name === "AbortError") return;
        setVista({ estado: "error", datos: null, error: e.message });
      });

    return () => control.abort();
  }, [pagina, estado, intento]);

  const puedePublicar = sesion?.rol === "REPRESENTANTE_DONANTE";
  const { datos } = vista;

  return (
    <section>
      <div className="acciones">
        <h1>Donaciones</h1>
        {puedePublicar && <Link className="btn" to="/donaciones/nueva">Publicar donación</Link>}
      </div>

      <div className="filtros">
        <label htmlFor="filtro-estado">Estado</label>
        <select id="filtro-estado" value={estado} onChange={(e) => { setEstado(e.target.value); setPagina(1); }}>
          {ESTADOS.map((valor) => (
            <option key={valor} value={valor}>{valor || "Todos"}</option>
          ))}
        </select>
      </div>

      {vista.estado === "cargando" && <p className="estado" role="status">Cargando donaciones...</p>}

      {vista.estado === "error" && (
        <div className="mensaje error" role="alert">
          {vista.error}{" "}
          <button className="btn sec" onClick={() => setIntento((n) => n + 1)}>Reintentar</button>
        </div>
      )}

      {vista.estado === "datos" && datos.results.length === 0 && (
        <p className="estado">No hay donaciones para mostrar.</p>
      )}

      {vista.estado === "datos" && datos.results.length > 0 && (
        <>
          <div className="tabla-contenedor">
            <table>
              <thead>
                <tr><th>Alimento</th><th>Cantidad</th><th>Fecha límite de retiro</th><th>Estado</th></tr>
              </thead>
              <tbody>
                {datos.results.map((d) => (
                  <tr key={d.id_donacion}>
                    <td>{d.alimento}{d.descripcion && <div className="ayuda">{d.descripcion}</div>}</td>
                    <td>{Number(d.cantidad)} {UNIDADES[d.unidad_medida] || d.unidad_medida}</td>
                    <td>{d.fecha_limite_retiro}</td>
                    <td><span className="etiqueta">{d.estado}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Paginacion pagina={datos.page} totalPaginas={datos.total_pages} total={datos.count} onCambiar={setPagina} />
        </>
      )}
    </section>
  );
}