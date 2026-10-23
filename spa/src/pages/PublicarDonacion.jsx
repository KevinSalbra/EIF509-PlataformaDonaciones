import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError, listarCategoriasActivas, publicarDonacion } from "../api/client.js";
import { useAuth } from "../auth/AuthContext.jsx";

const UNIDADES = [
  ["KILOGRAMO", "Kilogramo"], ["GRAMO", "Gramo"], ["LITRO", "Litro"],
  ["MILILITRO", "Mililitro"], ["UNIDAD", "Unidad"], ["PAQUETE", "Paquete"], ["CAJA", "Caja"],
];

const VACIO = {
  id_categoria: "", alimento: "", descripcion: "",
  cantidad: "", unidad_medida: "", fecha_limite_retiro: "",
};

function manana() {
  const fecha = new Date();
  fecha.setDate(fecha.getDate() + 1);
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return `${fecha.getFullYear()}-${mes}-${dia}`;
}

/** Validacion en el cliente; la API vuelve a validar todo. */
function validar(v) {
  const errores = {};
  if (!v.id_categoria) errores.id_categoria = "Seleccione una categoría.";
  if (!v.alimento.trim()) errores.alimento = "Ingrese el alimento.";
  else if (v.alimento.length > 150) errores.alimento = "Máximo 150 caracteres.";
  if (v.descripcion.length > 500) errores.descripcion = "Máximo 500 caracteres.";
  if (v.cantidad === "" || Number(v.cantidad) <= 0) errores.cantidad = "La cantidad debe ser mayor que cero.";
  if (!v.unidad_medida) errores.unidad_medida = "Seleccione la unidad de medida.";
  if (!v.fecha_limite_retiro) errores.fecha_limite_retiro = "Seleccione la fecha límite.";
  else if (v.fecha_limite_retiro < manana()) errores.fecha_limite_retiro = "Debe ser posterior a hoy.";
  return errores;
}

export default function PublicarDonacion() {
  const { sesion } = useAuth();
  const navigate = useNavigate();

  const [valores, setValores] = useState(VACIO);
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [categorias, setCategorias] = useState({ estado: "cargando", lista: [] });

  useEffect(() => {
    const control = new AbortController();
    listarCategoriasActivas(control.signal)
      .then((lista) => setCategorias({ estado: "datos", lista }))
      .catch((e) => {
        if (e.name !== "AbortError") setCategorias({ estado: "error", lista: [] });
      });
    return () => control.abort();
  }, []);

  if (sesion?.rol !== "REPRESENTANTE_DONANTE") {
    return (
      <section>
        <h1>Publicar donación</h1>
        <div className="mensaje error" role="alert">
          Solo los representantes de organizaciones donantes pueden publicar donaciones.
        </div>
        <Link className="btn sec" to="/donaciones">Volver</Link>
      </section>
    );
  }

  function cambiar(evento) {
    const { name, value } = evento.target;
    setValores((previos) => ({ ...previos, [name]: value }));
  }

  async function enviar(evento) {
    evento.preventDefault();
    setErrorGeneral("");

    const encontrados = validar(valores);
    setErrores(encontrados);
    if (Object.keys(encontrados).length > 0) return;

    setEnviando(true);
    try {
      await publicarDonacion({
        id_categoria: Number(valores.id_categoria),
        alimento: valores.alimento.trim(),
        descripcion: valores.descripcion.trim() || null,
        cantidad: valores.cantidad,
        unidad_medida: valores.unidad_medida,
        fecha_limite_retiro: valores.fecha_limite_retiro,
      });
      navigate("/donaciones", { replace: true });
    } catch (e) {
      if (e instanceof ApiError && e.errores) {
        // 400: errores por campo que devuelve la API.
        const delServidor = {};
        Object.entries(e.errores).forEach(([campo, mensajes]) => {
          delServidor[campo] = Array.isArray(mensajes) ? mensajes.join(" ") : String(mensajes);
        });
        setErrores(delServidor);
      } else {
        setErrorGeneral(e.message);
      }
    } finally {
      setEnviando(false);
    }
  }

  const campoError = (nombre) =>
    errores[nombre] && <p className="error-campo" role="alert">{errores[nombre]}</p>;

  return (
    <section>
      <h1>Publicar donación</h1>
      <form className="tarjeta" onSubmit={enviar} noValidate>
        {errorGeneral && <div className="mensaje error" role="alert">{errorGeneral}</div>}

        <div className="campo">
          <label htmlFor="id_categoria">Categoría</label>
          <select id="id_categoria" name="id_categoria" value={valores.id_categoria} onChange={cambiar} disabled={categorias.estado !== "datos"}>
            <option value="">
              {categorias.estado === "cargando" ? "Cargando..." : categorias.estado === "error" ? "No se pudieron cargar" : "Seleccione..."}
            </option>
            {categorias.lista.map((c) => (
              <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
            ))}
          </select>
          {campoError("id_categoria")}
        </div>

        <div className="campo">
          <label htmlFor="alimento">Alimento</label>
          <input id="alimento" name="alimento" type="text" maxLength={150} value={valores.alimento} onChange={cambiar} />
          {campoError("alimento")}
        </div>

        <div className="campo">
          <label htmlFor="descripcion">Descripción (opcional)</label>
          <textarea id="descripcion" name="descripcion" rows={3} maxLength={500} value={valores.descripcion} onChange={cambiar} />
          {campoError("descripcion")}
        </div>

        <div className="fila">
          <div className="campo">
            <label htmlFor="cantidad">Cantidad</label>
            <input id="cantidad" name="cantidad" type="number" min="0.01" step="0.01" value={valores.cantidad} onChange={cambiar} />
            {campoError("cantidad")}
          </div>
          <div className="campo">
            <label htmlFor="unidad_medida">Unidad</label>
            <select id="unidad_medida" name="unidad_medida" value={valores.unidad_medida} onChange={cambiar}>
              <option value="">Seleccione...</option>
              {UNIDADES.map(([valor, texto]) => <option key={valor} value={valor}>{texto}</option>)}
            </select>
            {campoError("unidad_medida")}
          </div>
        </div>

        <div className="campo">
          <label htmlFor="fecha_limite_retiro">Fecha límite de retiro</label>
          <input id="fecha_limite_retiro" name="fecha_limite_retiro" type="date" min={manana()} value={valores.fecha_limite_retiro} onChange={cambiar} />
          {campoError("fecha_limite_retiro")}
        </div>

        <div className="botones">
          <button className="btn" type="submit" disabled={enviando}>{enviando ? "Publicando..." : "Publicar"}</button>
          <Link className="btn sec" to="/donaciones">Cancelar</Link>
        </div>
      </form>
    </section>
  );
}