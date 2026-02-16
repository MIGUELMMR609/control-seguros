import { useEffect, useState } from "react";
import { getCompanias, getTipos } from "./api";

function PolizaForm({ onClose, onSave, token }) {
  const [companias, setCompanias] = useState([]);
  const [tipos, setTipos] = useState([]);

  const [form, setForm] = useState({
    compania: "",
    contacto_compania: "",
    telefono_compania: "",
    tipo: "",
    bien: "",
    numero_poliza: "",
    prima: "",
    fecha_inicio: "",
    fecha_vencimiento: "",
    estado: "activa"
  });

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      const dataCompanias = await getCompanias(token);
      const dataTipos = await getTipos(token);

      setCompanias(dataCompanias);
      setTipos(dataTipos);
    } catch (error) {
      alert("Error cargando datos");
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => {
    if (!form.compania || !form.tipo) {
      alert("Selecciona compañía y tipo");
      return;
    }

    onSave({
      ...form,
      prima: parseFloat(form.prima)
    });
  };

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h2>Nueva Póliza</h2>

        <label>Compañía:</label><br />
        <select name="compania" value={form.compania} onChange={handleChange}>
          <option value="">Seleccionar...</option>
          {companias.map(c => (
            <option key={c.id} value={c.nombre}>{c.nombre}</option>
          ))}
        </select><br /><br />

        <label>Contacto compañía:</label><br />
        <input name="contacto_compania" onChange={handleChange} /><br /><br />

        <label>Teléfono compañía:</label><br />
        <input name="telefono_compania" onChange={handleChange} /><br /><br />

        <label>Tipo:</label><br />
        <select name="tipo" value={form.tipo} onChange={handleChange}>
          <option value="">Seleccionar...</option>
          {tipos.map(t => (
            <option key={t.id} value={t.nombre}>{t.nombre}</option>
          ))}
        </select><br /><br />

        <label>Bien asegurado:</label><br />
        <input name="bien" onChange={handleChange} /><br /><br />

        <label>Número póliza:</label><br />
        <input name="numero_poliza" onChange={handleChange} /><br /><br />

        <label>Prima (€):</label><br />
        <input name="prima" type="number" onChange={handleChange} /><br /><br />

        <label>Fecha inicio:</label><br />
        <input name="fecha_inicio" type="date" onChange={handleChange} /><br /><br />

        <label>Fecha vencimiento:</label><br />
        <input name="fecha_vencimiento" type="date" onChange={handleChange} /><br /><br />

        <div style={{ marginTop: 20 }}>
          <button onClick={handleSubmit}>Guardar</button>{" "}
          <button onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  );
}

const overlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  backgroundColor: "rgba(0,0,0,0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center"
};

const modalStyle = {
  background: "white",
  padding: 30,
  borderRadius: 8,
  width: 400,
  maxHeight: "90vh",
  overflowY: "auto"
};

export default PolizaForm;
