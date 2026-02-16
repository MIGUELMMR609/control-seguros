import { useState } from "react";
import { loginRequest } from "./api";

function Login({ setToken }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError("");

    try {
      const data = await loginRequest(username, password);
      setToken(data.access_token);
    } catch (err) {
      setError("Usuario o contraseña incorrectos");
    }
  };

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

      <button onClick={handleLogin}>Entrar</button>

      {error && (
        <>
          <br /><br />
          <div style={{ color: "red" }}>{error}</div>
        </>
      )}
    </div>
  );
}

export default Login;
