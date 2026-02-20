import { useEffect, useState } from "react";
import { getPolizas, logout } from "./api";

export default function Dashboard({ onLogout }) {
  const [polizas, setPolizas] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getPolizas();
        setPolizas(data);
      } catch (err) {
        onLogout();
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <button onClick={() => { logout(); onLogout(); }}>
        Cerrar sesión
      </button>

      <ul>
        {polizas.map((p) => (
          <li key={p.id}>
            {p.numero_poliza} - {p.bien} - {p.fecha_vencimiento}
          </li>
        ))}
      </ul>
    </div>
  );
}