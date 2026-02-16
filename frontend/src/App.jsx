import { useState, useEffect } from "react";
import { loginRequest, getPolizas } from "./api";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [polizas, setPolizas] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (token) {
      cargarPolizas(token);
    }
  }, [token]);

  async function cargarPolizas(tk) {
    try {
      const data = await getPolizas(tk);
      setPolizas(data);
    } catch {
      setError("Error cargando pólizas");
    }
  }

  async function handleLogin() {
    setError("");
    try {
      const data = await loginRequest(username, password);
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
    } catch {
      setError("No se puede conectar con el servidor");
    }
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setPolizas([]);
  }

  if (!token) {
    return (
      <div style={{ padding: 20 }}>
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
        <button onClick={handleLogin}>Entrar</button>
        <p style={{ color: "red" }}>{error}</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Panel de Pólizas</h2>
      <button onClick={logout}>Cerrar sesión</button>
      <ul>
        {polizas.map((p) => (
          <li key={p.id}>{p.compania}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;

