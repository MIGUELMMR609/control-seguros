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
  const [sortConfig, setSortConfig] = useState({
    key: null,
    direction: "asc",
  });
  const [filterUrgent, setFilterUrgent] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

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

  const handleSort = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  const getArrow = (key) => {
    if (sortConfig.key !== key) return "";
    return sortConfig.direction === "asc" ? " ▲" : " ▼";
  };

  let processedPolizas = [...polizas];

  if (searchTerm) {
    processedPolizas = processedPolizas.filter(
      (p) =>
        p.numero_poliza.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.bien.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }

  if (filterUrgent) {
    processedPolizas = processedPolizas.filter(
      (p) => calcularDias(p.fecha_vencimiento) <= 30
    );

    processedPolizas.sort(
      (a, b) =>
        calcularDias(a.fecha_vencimiento) -
        calcularDias(b.fecha_vencimiento)
    );
  } else {
    processedPolizas.sort((a, b) => {
      if (!sortConfig.key) return 0;

      let valueA = a[sortConfig.key];
      let valueB = b[sortConfig.key];

      if (sortConfig.key.includes("fecha")) {
        valueA = new Date(valueA);
        valueB = new Date(valueB);
      }

      if (valueA < valueB)
        return sortConfig.direction === "asc" ? -1 : 1;
      if (valueA > valueB)
        return sortConfig.direction === "asc" ? 1 : -1;

      return 0;
    });
  }

  const totalUrgentes = polizas.filter(
    (p) => calcularDias(p.fecha_vencimiento) <= 30
  ).length;

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h2>Dashboard</h2>

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
        <input placeholder="Número póliza"
          value={form.numero_poliza}
          onChange={(e)=>setForm({...form,numero_poliza:e.target.value})}
          required />

        <input placeholder="Bien"
          value={form.bien}
          onChange={(e)=>setForm({...form,bien:e.target.value})}
          required />

        <input type="number" placeholder="Prima"
          value={form.prima}
          onChange={(e)=>setForm({...form,prima:e.target.value})}
          required />

        <input type="date"
          value={form.fecha_inicio}
          onChange={(e)=>setForm({...form,fecha_inicio:e.target.value})}
          required />

        <input type="date"
          value={form.fecha_vencimiento}
          onChange={(e)=>setForm({...form,fecha_vencimiento:e.target.value})}
          required />

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
            <th>Último aviso</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {processedPolizas.map((p) => {
            const dias = calcularDias(p.fecha_vencimiento);
            const progreso = calcularProgreso(p.fecha_vencimiento);
            const color = getColor(dias);

            return (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>{p.numero_poliza}</td>
                <td>{p.bien}</td>
                <td>{p.prima}</td>
                <td>
                  {p.fecha_vencimiento} ({dias} días)
                  <div style={{height:"6px",background:"#eee"}}>
                    <div style={{
                      height:"6px",
                      width:`${progreso}%`,
                      background:color
                    }} />
                  </div>
                </td>
                <td>
                  {p.fecha_aviso_enviado
                    ? new Date(p.fecha_aviso_enviado).toLocaleString()
                    : "-"}
                </td>
                <td>
                  <button onClick={()=>handleEdit(p)}>Editar</button>
                  <button onClick={()=>handleDelete(p.id)}>Eliminar</button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}