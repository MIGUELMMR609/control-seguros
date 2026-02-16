import { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [polizas, setPolizas] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      cargarPolizas(token);
    }
  }, [token]);

  const iniciarSesion = async () => {
    setError("");
    setLoading(true);

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

      if (response.status === 401) {
        setError("Credenciales incorrectas");
        setLoading(false);
        return;
      }

      if (!response.ok) {
        setError("Error del servidor");
        setLoading(false);
        return;
      }

      const data = await response.json();

      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);

    } catch {
      setError("No se puede conectar con el servidor");
    }

    setLoading(false);
  };

  const cerrarSesion = () => {
    localStorage.removeItem("token");
    setToken(null);
    setPolizas([]);
  };

  const cargarPolizas = async (authToken) => {
    try {
      const response = await fetch(`${API}/polizas`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (response.status === 401) {
        cerrarSesion();
        return;
      }

      if (!response.ok) {
        setError("Error al cargar pólizas");
        return;
      }

      const dataPolizas = await response.json();
      setPolizas(dataPolizas);

    } catch {
      setError("Error de conexión cargando pólizas");
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

        <button onClick={iniciarSesion} disabled={loading}>
          {loading ? "Entrando..." : "Entrar"}
        </button>

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

      <button onClick={cerrarSesion}>Cerrar sesión</button>

      {error && <div style={{ color: "red" }}>{error}</div>}

      <ul>
        {polizas.map((p) => (
          <li key={p.id}>
            {p.compania} - {p.bien} - {p.prima}€
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
