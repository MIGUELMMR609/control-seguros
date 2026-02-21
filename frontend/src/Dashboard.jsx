import { useEffect, useState } from "react";
import {
  getPolizas,
  createPoliza,
  updatePoliza,
  deletePoliza,
  logout,
} from "./api";

const API_URL = "https://control-seguros-backend-pro.onrender.com";

export default function Dashboard({ onLogout }) {
  const [polizas, setPolizas] = useState([]);
  const [avisos, setAvisos] = useState({});
  const [expanded, setExpanded] = useState(null);

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

  const loadAvisos = async (polizaId) => {
    const token = localStorage.getItem("token");

    const response = await fetch(
      `${API_URL}/polizas/${polizaId}/avisos`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const data = await response.json();

    setAvisos((prev) => ({
      ...prev,
      [polizaId]: data,
    }));
  };

  const toggleExpand = async (id) => {
    if (expanded === id) {
      setExpanded(null);
    } else {
      await loadAvisos(id);
      setExpanded(id);
    }
  };

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

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h2>Dashboard V3</h2>

      <button
        onClick={() => {
          logout();
          onLogout();
        }}
      >
        Cerrar sesión
      </button>

      <hr />

      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <input
          placeholder="Número póliza"
          value={form.numero_poliza}
          onChange={(e) =>
            setForm({ ...form, numero_poliza: e.target.value })
          }
          required
        />

        <input
          placeholder="Bien"
          value={form.bien}
          onChange={(e) =>
            setForm({ ...form, bien: e.target.value })
          }
          required
        />

        <input
          type="number"
          placeholder="Prima"
          value={form.prima}
          onChange={(e) =>
            setForm({ ...form, prima: e.target.value })
          }
          required
        />

        <input
          type="date"
          value={form.fecha_inicio}
          onChange={(e) =>
            setForm({ ...form, fecha_inicio: e.target.value })
          }
          required
        />

        <input
          type="date"
          value={form.fecha_vencimiento}
          onChange={(e) =>
            setForm({ ...form, fecha_vencimiento: e.target.value })
          }
          required
        />

        <button type="submit">
          {editingId ? "Actualizar" : "Crear"}
        </button>
      </form>

      <table style={{ borderCollapse: "collapse", width: "100%" }}>
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
            <>
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
                  <button onClick={() => toggleExpand(p.id)}>
                    Historial avisos
                  </button>
                </td>
              </tr>

              {expanded === p.id && (
                <tr>
                  <td colSpan="6">
                    <strong>Histórico:</strong>
                    <ul>
                      {avisos[p.id]?.length === 0 && (
                        <li>No hay avisos enviados</li>
                      )}
                      {avisos[p.id]?.map((a) => (
                        <li key={a.id}>
                          Aviso {a.tipo_aviso} días —{" "}
                          {new Date(a.fecha_envio).toLocaleString()}
                        </li>
                      ))}
                    </ul>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
}