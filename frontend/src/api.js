const API_URL = "https://control-seguros-backend-pro.onrender.com";

const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
};

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

  if (!response.ok) throw new Error("Credenciales incorrectas");

  const data = await response.json();
  localStorage.setItem("token", data.access_token);
};

export const getPolizas = async () => {
  const response = await fetch(`${API_URL}/polizas`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error("Error cargando pólizas");

  return response.json();
};

export const createPoliza = async (poliza) => {
  const response = await fetch(`${API_URL}/polizas`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(poliza),
  });

  if (!response.ok) throw new Error("Error creando póliza");
};

export const updatePoliza = async (id, poliza) => {
  const response = await fetch(`${API_URL}/polizas/${id}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(poliza),
  });

  if (!response.ok) throw new Error("Error actualizando póliza");
};

export const deletePoliza = async (id) => {
  const response = await fetch(`${API_URL}/polizas/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error("Error eliminando póliza");
};

export const logout = () => {
  localStorage.removeItem("token");
};