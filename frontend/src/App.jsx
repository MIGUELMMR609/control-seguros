import { useState } from "react";

const API = "https://control-seguros-api.onrender.com";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [polizas, setPolizas] = useState([]);

  const iniciarSesion = async () => {
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
  };

  const cargarPolizas = async (authToken) => {
    const response = await fetch(
      `${API}/polizas?token=${authToken}`
    );

    if (!response.ok) {
      alert("Error cargando pólizas");
      return;
    }

    const data = await response.json();
    setPolizas(data);
  };

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

  return (
    <div style={{ padding: 40 }}>
      <h1>Pólizas</h1>
      {polizas.length === 0 && <p>No hay pólizas</p>}
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
