import { useState } from "react";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);

  const [polizas, setPolizas] = useState([]);
  const [vista, setVista] = useState("dashboard");

  const [compania, setCompania] = useState("");
  const [bien, setBien] = useState("");
  const [precio, setPrecio] = useState("");
  const [fecha, setFecha] = useState("");
  const [editandoId, setEditandoId] = useState(null);

  // ---------------- LOGIN ----------------

  const iniciarSesion = () => {
    fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }),
    })
      .then((res) => {
        if (!res.ok) {
          alert("Usuario o contraseña incorrectos");
          return;
        }
        return res.json();
      })
      .then((data) => {
        if (data?.access_token) {
          setToken(data.access_token);
          cargarPolizas(data.access_token);
        }
      });
  };

  const cargarPolizas = (authToken) => {
    fetch("http://127.0.0.1:8000/polizas", {
      headers: { Authorization: `Bearer ${authToken}` },
    })
      .then((res) => res.json())
      .then((data) => setPolizas(data));
  };

  // ---------------- CALCULOS ----------------

  const calcularDias = (fechaVenc) => {
    const hoy = new Date();
    const venc = new Date(fechaVenc);
    return Math.ceil((venc - hoy) / (1000 * 60 * 60 * 24));
  };

  const totalImporte = polizas.reduce((acc, p) => acc + p.precio, 0);

  const proximas = polizas.filter(
    (p) => calcularDias(p.fecha_vencimiento) <= 15 &&
           calcularDias(p.fecha_vencimiento) >= 0
  );

  const vencidas = polizas.filter(
    (p) => calcularDias(p.fecha_vencimiento) < 0
  );

  const formatearFecha = (fechaISO) =>
    new Date(fechaISO).toLocaleDateString("es-ES");

  const colorFila = (dias) => {
    if (dias < 0) return "#ffcccc";
    if (dias <= 15) return "#fff3cd";
    return "#d4edda";
  };

  const cardStyle = (color) => ({
    backgroundColor: color,
    color: "white",
    padding: "25px",
    borderRadius: "12px",
    textAlign: "center",
    boxShadow: "0 5px 15px rgba(0,0,0,0.2)"
  });

  // ---------------- CRUD ----------------

  const guardarPoliza = () => {
    if (!compania || !bien || !precio || !fecha) {
      alert("Todos los campos son obligatorios");
      return;
    }

    const metodo = editandoId ? "PUT" : "POST";
    const url = editandoId
      ? `http://127.0.0.1:8000/polizas/${editandoId}`
      : "http://127.0.0.1:8000/polizas";

    fetch(url, {
      method: metodo,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        compania,
        bien,
        precio: parseFloat(precio),
        fecha_vencimiento: fecha,
      }),
    }).then(() => {
      setCompania("");
      setBien("");
      setPrecio("");
      setFecha("");
      setEditandoId(null);
      cargarPolizas(token);
    });
  };

  const eliminarPoliza = (id) => {
    fetch(`http://127.0.0.1:8000/polizas/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    }).then(() => cargarPolizas(token));
  };

  const editarPoliza = (poliza) => {
    setVista("gestion");
    setCompania(poliza.compania);
    setBien(poliza.bien);
    setPrecio(poliza.precio);
    setFecha(poliza.fecha_vencimiento);
    setEditandoId(poliza.id);
  };

  // ---------------- LOGIN VIEW ----------------

  if (!token) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Iniciar Sesión</h2>
        <input
          placeholder="Usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        /><br /><br />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        /><br /><br />
        <button onClick={iniciarSesion}>Entrar</button>
      </div>
    );
  }

  // ---------------- DASHBOARD ----------------

  if (vista === "dashboard") {
    return (
      <div style={{ padding: 40 }}>
        <h1>Dashboard Control de Seguros</h1>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "20px",
          marginTop: "30px"
        }}>
          <div style={cardStyle("#2563eb")}>
            <h3>Total Pólizas</h3>
            <h2>{polizas.length}</h2>
          </div>

          <div style={cardStyle("#16a34a")}>
            <h3>Importe Total</h3>
            <h2>{totalImporte} €</h2>
          </div>

          <div style={cardStyle("#f59e0b")}>
            <h3>Vencen en 15 días</h3>
            <h2>{proximas.length}</h2>
          </div>

          <div style={cardStyle("#dc2626")}>
            <h3>Vencidas</h3>
            <h2>{vencidas.length}</h2>
          </div>
        </div>

        <br /><br />

        <button
          onClick={() => setVista("gestion")}
          style={{
            padding: "12px 25px",
            backgroundColor: "#1e3a8a",
            color: "white",
            border: "none",
            borderRadius: "10px",
            fontSize: "16px",
            cursor: "pointer"
          }}
        >
          Gestionar pólizas
        </button>
      </div>
    );
  }

  // ---------------- GESTION ----------------

  return (
    <div style={{ padding: 40 }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <h1>Gestión de Pólizas</h1>
        <button
          onClick={() => setVista("dashboard")}
          style={{
            padding: "10px 20px",
            backgroundColor: "#1e3a8a",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer"
          }}
        >
          ← Volver al Dashboard
        </button>
      </div>

      <hr />

      <input
        placeholder="Compañía"
        value={compania}
        onChange={(e) => setCompania(e.target.value)}
      /><br /><br />

      <input
        placeholder="Bien"
        value={bien}
        onChange={(e) => setBien(e.target.value)}
      /><br /><br />

      <input
        placeholder="Precio"
        value={precio}
        onChange={(e) => setPrecio(e.target.value)}
      /><br /><br />

      <input
        type="date"
        value={fecha}
        onChange={(e) => setFecha(e.target.value)}
      /><br /><br />

      <button onClick={guardarPoliza}>
        {editandoId ? "Actualizar" : "Guardar"}
      </button>

      <hr />

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Compañía</th>
            <th>Bien</th>
            <th>Precio</th>
            <th>Vencimiento</th>
            <th>Días</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {polizas.map((poliza) => {
            const dias = calcularDias(poliza.fecha_vencimiento);
            return (
              <tr key={poliza.id} style={{ backgroundColor: colorFila(dias) }}>
                <td>{poliza.compania}</td>
                <td>{poliza.bien}</td>
                <td>{poliza.precio} €</td>
                <td>{formatearFecha(poliza.fecha_vencimiento)}</td>
                <td>{dias}</td>
                <td>
                  <button onClick={() => editarPoliza(poliza)}>Editar</button>
                  <button onClick={() => eliminarPoliza(poliza.id)}>Eliminar</button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default App;
