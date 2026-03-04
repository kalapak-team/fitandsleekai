import axios from "axios";
import { resolveApiBaseUrl } from "../lib/backendOrigin";

const baseURL = resolveApiBaseUrl();
const TOKEN_KEY = import.meta.env.VITE_TOKEN_KEY || "fs_token";

const api = axios.create({
  baseURL,
  headers: { Accept: "application/json" },
});

// attach Bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
export { TOKEN_KEY };
