import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  borrarToken,
  guardarToken,
  iniciarSesion,
  obtenerToken,
  registrarAlNoAutorizado,
} from "../api/client.js";

const AuthContext = createContext(null);

/** Lee los datos del JWT (solo para la interfaz; la API es quien valida). */
function leerPayload(token) {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
        .join("")
    );
    const payload = JSON.parse(json);
    if (payload.exp && payload.exp * 1000 < Date.now()) return null;
    return payload;
  } catch {
    return null;
  }
}

function sesionDesdeToken(token) {
  if (!token) return null;
  const payload = leerPayload(token);
  return payload ? { rol: payload.rol, idOrganizacion: payload.id_organizacion } : null;
}

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [sesion, setSesion] = useState(() => {
    const sesionInicial = sesionDesdeToken(obtenerToken());
    if (!sesionInicial) borrarToken();
    return sesionInicial;
  });
  const [aviso, setAviso] = useState("");

  const cerrarSesion = useCallback(() => {
    borrarToken();
    setSesion(null);
  }, []);

  // Cliente HTTP: ante un 401 se cierra la sesion y se vuelve al login.
  useEffect(() => {
    registrarAlNoAutorizado(() => {
      setSesion(null);
      setAviso("Su sesión expiró. Inicie sesión nuevamente.");
      navigate("/login", { replace: true });
    });
  }, [navigate]);

  const login = useCallback(async (correo, contrasena) => {
    const { access_token: token } = await iniciarSesion(correo, contrasena);
    guardarToken(token);
    setSesion(sesionDesdeToken(token));
    setAviso("");
  }, []);

  const valor = useMemo(
    () => ({ sesion, aviso, login, cerrarSesion }),
    [sesion, aviso, login, cerrarSesion]
  );

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}