import { useState } from "react";

const API = "https://control-seguros-api.onrender.com";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [polizas, setPolizas] = useState([]);
  const [error, setError] = useState("");

  const iniciarSesion = async () => {
    setError("");

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
        setError("Usuario o contraseña incorrectos");
        return;
      }

      const data = await response.json();

      if (!data.access_token) {
        setError("No se recibió token del servidor");
        return;
      }

      setToken(data.access_token);
      cargarPolizas(data.access_token);

    } catch (err) {
      setError("Error de conexión con el servidor");
    }
  };

  const cargarPolizas = async (authToken) => {
    try {
      const response = await fetch(
        `${API}/polizas?token=${authToken}`
      );

      if (!response.ok) {
        setError("Error al cargar pólizas");
        return;
      }

      const data = await response.json();

      if (!Array.isArray(data)) {
        setError("Formato de datos incorrecto");
        return;
      }

      setPolizas(data);

    } catch (err) {
      setError("Error al obtener pólizas");
    }
  };

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

        <button onClick={iniciarSesion}>Entrar</button>

        {error && (
          <>
            <br /><br />
            <div style={{ color: "red" }}>{error}</div>
          </>
        )}
      </div>
    );
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>Pólizas</h1>

      {error && (
        <div style={{ color: "red" }}>{error}</div>
      )}

      <ul>
        {polizas.map((p) => (
          <li key={p.id}>
            {p.compania} - {p.bien} - {p.precio}€
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
