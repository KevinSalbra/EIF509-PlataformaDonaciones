import { Link, Navigate, Route, Routes } from "react-router-dom";

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
          <span className="marca">AlimentaCR</span>
          {sesion && (
            <>
              <nav aria-label="Secciones">
                <Link to="/donaciones">Donaciones</Link>
              </nav>
              <button className="salir" onClick={cerrarSesion}>Cerrar sesión</button>
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