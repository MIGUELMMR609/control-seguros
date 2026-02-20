import { useEffect, useState } from "react";
import {
  getPolizas,
  createPoliza,
  updatePoliza,
  deletePoliza,
  logout,
} from "./api";

export default function Dashboard({ onLogout }) {
  const [polizas, setPolizas] = useState([]);
  const [form, setForm] = useState({
    numero_poliza: "",
    bien: "",
    prima: "",
    fecha_inicio: "",
    fecha_vencimiento: "",
  });
  const [editingId, setEditingId] = useState(null);

  const loadData = async () => {
    const data = await getPolizas();
    setPolizas(data);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      ...form,
      prima: parseFloat(form.prima),
    };

    if (editingId) {
      await updatePoliza(editingId, payload);
      setEditingId(null);
    } else {
      await createPoliza(payload);
    }

    setForm({
      numero_poliza: "",
      bien: "",
      prima: "",
      fecha_inicio: "",
      fecha_vencimiento: "",
    });

    loadData();
  };

  const handleEdit = (p) => {
    setForm({
      numero_poliza: p.numero_poliza,
      bien: p.bien,
      prima: p.prima,
      fecha_inicio: p.fecha_inicio?.split("T")[0],
      fecha_vencimiento: p.fecha_vencimiento?.split("T")[0],
    });

    setEditingId(p.id);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("¿Seguro que quieres eliminar esta póliza?")) return;
    await deletePoliza(id);
    loadData();
  };

  // 🔥 NUEVO CÁLCULO 30 DÍAS O MENOS
  const hoy = new Date();

  const proximas = polizas.filter((p) => {
    const venc = new Date(p.fecha_vencimiento);
    const diffTime = venc - hoy;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 30 && diffDays >= 0;
  });

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h2>Dashboard</h2>

      <button
        onClick={() => {
          logout();
          onLogout();
        }}
      >
        Cerrar sesión
      </button>

      <hr />

      {/* 🔴 SECCIÓN 30 DÍAS O MENOS */}
      {proximas.length > 0 && (
        <div
          style={{
            backgroundColor: "#ffe5e5",
            padding: "15px",
            marginBottom: "20px",
            border: "1px solid red",
          }}
        >
          <h3 style={{ color: "red" }}>
            ⚠️ Pólizas que vencen en 30 días o menos
          </h3>
          <ul>
            {proximas.map((p) => (
              <li key={p.id}>
                {p.numero_poliza} - {p.bien} - {p.fecha_vencimiento}
              </li>
            ))}
          </ul>
        </div>
      )}

      <h3>{editingId ? "Editar póliza" : "Nueva póliza"}</h3>

      <form onSubmit={handleSubmit} style={{ marginBottom: "30px" }}>
        <input
          placeholder="Número"
          value={form.numero_poliza}
          onChange={(e) =>
            setForm({ ...form, numero_poliza: e.target.value })
          }
        />
        <input
          placeholder="Bien"
          value={form.bien}
          onChange={(e) => setForm({ ...form, bien: e.target.value })}
        />
        <input
          placeholder="Prima"
          type="number"
          value={form.prima}
          onChange={(e) => setForm({ ...form, prima: e.target.value })}
        />
        <input
          type="date"
          value={form.fecha_inicio}
          onChange={(e) =>
            setForm({ ...form, fecha_inicio: e.target.value })
          }
        />
        <input
          type="date"
          value={form.fecha_vencimiento}
          onChange={(e) =>
            setForm({ ...form, fecha_vencimiento: e.target.value })
          }
        />
        <button type="submit">
          {editingId ? "Actualizar" : "Crear"}
        </button>
      </form>

      <h3>Listado</h3>

      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Número</th>
            <th>Bien</th>
            <th>Prima</th>
            <th>Vencimiento</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {polizas.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.numero_poliza}</td>
              <td>{p.bien}</td>
              <td>{p.prima}</td>
              <td>{p.fecha_vencimiento}</td>
              <td>
                <button onClick={() => handleEdit(p)}>Editar</button>
                <button onClick={() => handleDelete(p.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}