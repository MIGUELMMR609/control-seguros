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

  const hoy = new Date();

  const calcularDias = (fecha) => {
    const venc = new Date(fecha);
    const diffTime = venc - hoy;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const calcularProgreso = (fecha) => {
    const dias = calcularDias(fecha);
    const total = 30;
    const restante = Math.max(0, Math.min(total, dias));
    return 100 - (restante / total) * 100;
  };

  const getColor = (dias) => {
    if (dias <= 7 && dias >= 0) return "#d32f2f";
    if (dias <= 15 && dias >= 0) return "#f57c00";
    if (dias <= 30 && dias >= 0) return "#fbc02d";
    return "#4caf50";
  };

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

  const totalUrgentes = polizas.filter(
    (p) => calcularDias(p.fecha_vencimiento) <= 30
  ).length;

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h2>Dashboard V3</h2>

      {totalUrgentes > 0 && (
        <div
          style={{
            background: "#ffebee",
            color: "#c62828",
            padding: "10px",
            borderRadius: "6px",
            marginBottom: "15px",
            fontWeight: "bold",
          }}
        >
          🔴 {totalUrgentes} pólizas próximas a vencer
        </div>
      )}

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
          {polizas.map((p) => {
            const dias = calcularDias(p.fecha_vencimiento);
            const progreso = calcularProgreso(p.fecha_vencimiento);
            const color = getColor(dias);

            return (
              <>
                <tr key={p.id}>
                  <td>{p.id}</td>
                  <td>{p.numero_poliza}</td>
                  <td>{p.bien}</td>
                  <td>{p.prima}</td>
                  <td style={{ minWidth: "220px" }}>
                    {p.fecha_vencimiento}{" "}
                    {dias >= 0 && (
                      <span style={{ fontSize: "0.85em", color }}>
                        ({dias} días)
                      </span>
                    )}

                    <div
                      style={{
                        height: "6px",
                        background: "#eee",
                        borderRadius: "4px",
                        marginTop: "6px",
                      }}
                    >
                      <div
                        style={{
                          height: "6px",
                          width: `${progreso}%`,
                          background: color,
                          borderRadius: "4px",
                        }}
                      />
                    </div>
                  </td>
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
            );
          })}
        </tbody>
      </table>
    </div>
  );
}