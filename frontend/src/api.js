const API_URL = "https://control-seguros-backend-pro.onrender.com";

export const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Credenciales incorrectas");
  }

  const data = await response.json();
  localStorage.setItem("token", data.access_token);
  return data;
};

export const getPolizas = async () => {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/polizas`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("No autorizado");
  }

  return response.json();
};

export const logout = () => {
  localStorage.removeItem("token");
};