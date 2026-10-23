import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext.jsx";

export default function Login() {
  const { sesion, aviso, login } = useAuth();
  const navigate = useNavigate();
  const ubicacion = useLocation();

  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  if (sesion) return <Navigate to="/donaciones" replace />;

  async function enviar(evento) {
    evento.preventDefault();
    setError("");

    if (!correo.trim() || !contrasena) {
      setError("Ingrese su correo y contraseña.");
      return;
    }

    setEnviando(true);
    try {
      await login(correo.trim(), contrasena);
      navigate(ubicacion.state?.desde || "/donaciones", { replace: true });
    } catch (e) {
      setError(e.status === 401 ? "Credenciales inválidas." : e.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section>
      <h1>Iniciar sesión</h1>
      {aviso && <div className="mensaje" role="status">{aviso}</div>}
      <form className="tarjeta" onSubmit={enviar} noValidate>
        {error && <div className="mensaje error" role="alert">{error}</div>}
        <div className="campo">
          <label htmlFor="correo">Correo</label>
          <input id="correo" type="email" autoComplete="username" value={correo} onChange={(e) => setCorreo(e.target.value)} />
        </div>
        <div className="campo">
          <label htmlFor="contrasena">Contraseña</label>
          <input id="contrasena" type="password" autoComplete="current-password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={enviando}>
          {enviando ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </section>
  );
}