import { NavLink, Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./auth/AuthContext.jsx";
import RutaProtegida from "./components/RutaProtegida.jsx";
import Donaciones from "./pages/Donaciones.jsx";
import Login from "./pages/Login.jsx";
import PublicarDonacion from "./pages/PublicarDonacion.jsx";

export default function App() {
  const { sesion, cerrarSesion } = useAuth();

  return (
    <>
      <header>
        <div className="barra">
          <span className="marca">
            <span className="logo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" /><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" /></svg></span>
            AlimentaCR
          </span>
          {sesion && (
            <>
              <nav aria-label="Secciones">
                <NavLink to="/donaciones">Donaciones</NavLink>
              </nav>
              <button className="salir" type="button" onClick={cerrarSesion}>Cerrar sesión</button>
            </>
          )}
        </div>
      </header>
      <main>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/donaciones" element={<RutaProtegida><Donaciones /></RutaProtegida>} />
          <Route path="/donaciones/nueva" element={<RutaProtegida><PublicarDonacion /></RutaProtegida>} />
          <Route path="*" element={<Navigate to="/donaciones" replace />} />
        </Routes>
      </main>
    </>
  );
}