import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../auth/AuthContext.jsx";

export default function RutaProtegida({ children }) {
  const { sesion } = useAuth();
  const ubicacion = useLocation();

  if (!sesion) {
    return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />;
  }
  return children;
}