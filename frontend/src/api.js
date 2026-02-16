const API = "http://127.0.0.1:8000";

export async function loginRequest(username, password) {
  const body = new URLSearchParams();
  body.append("grant_type", "password");
  body.append("username", username);
  body.append("password", password);
  body.append("scope", "");
  body.append("client_id", "string");
  body.append("client_secret", "string");

  const response = await fetch(`${API}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  if (!response.ok) {
    throw new Error("Credenciales incorrectas");
  }

  return response.json();
}

export async function getPolizas(token) {
  const response = await fetch(`${API}/polizas`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Error al cargar pólizas");
  }

  return response.json();
}
