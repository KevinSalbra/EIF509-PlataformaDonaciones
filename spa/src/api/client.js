/**
 * Cliente HTTP
 *
 * Todas las llamadas a la API pasan por request(): aqui se agrega el
 * token JWT, se interpretan los errores (Problem Details) y se maneja
 * el 401 en un solo lugar.
 */

const BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const CLAVE_TOKEN = "alimentacr_token";

// --- Token (sessionStorage: se borra al cerrar la pestana) -------------

export function obtenerToken() {
  try {
    return sessionStorage.getItem(CLAVE_TOKEN);
  } catch {
    return null;
  }
}

export function guardarToken(token) {
  try {
    sessionStorage.setItem(CLAVE_TOKEN, token);
  } catch {
    /* almacenamiento no disponible */
  }
}

export function borrarToken() {
  try {
    sessionStorage.removeItem(CLAVE_TOKEN);
  } catch {
    /* almacenamiento no disponible */
  }
}

// --- Manejo del 401 -----------------------------------------------------

let alNoAutorizado = () => {};

/** AuthContext registra aqui que hacer cuando la API responde 401. */
export function registrarAlNoAutorizado(callback) {
  alNoAutorizado = callback;
}

// --- Errores ------------------------------------------------------------

export class ApiError extends Error {
  constructor(status, detalle, errores = null) {
    super(detalle);
    this.name = "ApiError";
    this.status = status;
    this.errores = errores; // errores por campo (400), si los hay
  }
}

function mensajePorDefecto(status) {
  if (status === 0) return "No se pudo conectar con el servidor.";
  if (status === 403) return "No tiene permiso para realizar esta acción.";
  if (status === 404) return "No se encontró el recurso solicitado.";
  if (status >= 500) return "Error interno del servidor. Intente más tarde.";
  return "No se pudo completar la solicitud.";
}

// --- Peticion base --------------------------------------------------------

/**
 * @param {string} ruta  Ej. "/api/v1/donaciones"
 * @param {{method?: string, body?: object, params?: object,
 *          autenticada?: boolean, signal?: AbortSignal}} opciones
 */
export async function request(ruta, opciones = {}) {
  const { method = "GET", body, params, autenticada = true, signal } = opciones;

  const url = new URL(BASE_URL + ruta);
  Object.entries(params || {}).forEach(([clave, valor]) => {
    if (valor !== undefined && valor !== null && valor !== "") {
      url.searchParams.set(clave, valor);
    }
  });

  const encabezados = { Accept: "application/json" };
  if (body !== undefined) encabezados["Content-Type"] = "application/json";

  const token = obtenerToken();
  if (autenticada && token) encabezados.Authorization = `Bearer ${token}`;

  let respuesta;
  try {
    respuesta = await fetch(url, {
      method,
      headers: encabezados,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new ApiError(0, mensajePorDefecto(0));
  }

  let datos = null;
  const texto = await respuesta.text();
  if (texto) {
    try {
      datos = JSON.parse(texto);
    } catch {
      datos = null;
    }
  }

  if (!respuesta.ok) {
    // 401 con sesion iniciada = token vencido o invalido: cerrar sesion.
    if (respuesta.status === 401 && autenticada && token) {
      borrarToken();
      alNoAutorizado();
    }
    throw new ApiError(
      respuesta.status,
      (datos && datos.detail) || mensajePorDefecto(respuesta.status),
      datos && datos.errores ? datos.errores : null
    );
  }

  return datos;
}

// --- Operaciones de la API -------------------------------------------------

export function iniciarSesion(correo, contrasena) {
  return request("/api/v1/auth/login", {
    method: "POST",
    body: { correo, contrasena },
    autenticada: false,
  });
}

export function listarDonaciones({ page = 1, pageSize = 10, estado, ordering } = {}, signal) {
  return request("/api/v1/donaciones", {
    params: { page, page_size: pageSize, estado, ordering },
    autenticada: false,
    signal,
  });
}

export function listarCategoriasActivas(signal) {
  return request("/api/v1/categorias/activas", { signal });
}

export function publicarDonacion(datos) {
  return request("/api/v1/donaciones/publicar", { method: "POST", body: datos });
}