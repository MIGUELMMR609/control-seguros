import { useEffect, useState } from "react";
import { getPolizas } from "./api";

function PolizasList({ token }) {
  const [polizas, setPolizas] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    cargarPolizas();
  }, []);

  const cargarPolizas = async () => {
    try {
      const data = await getPolizas(token);
      setPolizas(data);
    } catch (err) {
      setError("Error al cargar pólizas");
    }
  };

  const calcularDias = (fecha) => {
    const hoy = new Date();
    const venc = new Date(fecha);
    const diff = venc - hoy;
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  return (
    <div>
      <h2>Pólizas</h2>

      {error && <div style={{ color: "red" }}>{error}</div>}

      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Compañía</th>
            <th>Tipo</th>
            <th>Bien</th>
            <th>Nº Póliza</th>
            <th>Prima (€)</th>
            <th>Vencimiento</th>
            <th>Días restantes</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {polizas.map((p) => (
            <tr key={p.id}>
              <td>{p.compania?.nombre || p.compania}</td>
              <td>{p.tipo?.nombre || p.tipo}</td>
              <td>{p.bien}</td>
              <td>{p.numero_poliza}</td>
              <td>{p.prima}</td>
              <td>{p.fecha_vencimiento}</td>
              <td>{calcularDias(p.fecha_vencimiento)}</td>
              <td>{p.estado}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PolizasList;
