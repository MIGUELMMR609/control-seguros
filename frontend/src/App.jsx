import { useState } from "react";

const API = "https://control-seguros-api.onrender.com";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [polizas, setPolizas] = useState([]);

  // ---------------- LOGIN ----------------

  const iniciarSesion = async () => {
    try {
      const response = await fetch(`${API}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          grant_type: "password",
          username: username,
          password: password,
        }),
      });

      if (!response.ok) {
        alert("Usuario o contraseña incorrectos");
        return;
      }

      const data = await response.json();
      setToken(data.access_token);

      cargarPolizas(data.access_token);

    } catch (error) {
      console.error("Error login:", error);
    }
  };

  // ---------------- CARGAR POLIZAS ----------------

  const cargarPolizas = async (authToken) => {
    try {
      const response = await fetch(`${API}/polizas`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      // 🔴 Si el backend devuelve error (ej 422), no rompemos la app
      if (!response.ok) {
        console.log("Error al cargar pólizas:", response.status);
        setPolizas([]);
        return;
      }

      const data = await response.json();

      // 🔴 Si por cualquier motivo no es array
      if (!Array.isArray(data)) {
        console.log("La respuesta no es un array");
        setPolizas([]);
        return;
      }

      setPolizas(data);

    } catch (error) {
      console.error("Error fetch polizas:", error);
      setPolizas([]);
    }
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
        />
        <br /><br />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <br /><br />

        <button onClick={iniciarSesion}>
          Entrar
        </button>
      </div>
    );
  }

  // ---------------- POLIZAS VIEW ----------------

  return (
    <div style={{ padding: 40 }}>
      <h1>Pólizas</h1>

      {polizas.length === 0 ? (
        <p>No hay pólizas registradas.</p>
      ) : (
        <ul>
          {polizas.map((p) => (
            <li key={p.id}>
              {p.compania} - {p.bien} - {p.precio}€
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
