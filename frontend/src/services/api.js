import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("itms_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (typeof window !== "undefined" && error.response?.status === 401) {
      localStorage.removeItem("itms_token");
      localStorage.removeItem("itms_user");
      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email, password) => api.post("/v1/auth/login", { email, password }),
  register: (payload) => api.post("/v1/auth/register", payload),
  me: () => api.get("/v1/auth/me")
};

export const dashboardApi = {
  getOverview: () => api.get("/v1/junctions/stats/overview"),
  getSystemState: () => api.get("/v1/system/state")
};

export const usersApi = {
  list: () => api.get("/users"),
  update: (id, payload) => api.put(`/users/${id}`, payload)
};

export const junctionsApi = {
  list: () => api.get("/v1/junctions"),
  create: (payload) => api.post("/v1/junctions", payload),
  update: (id, payload) => api.put(`/v1/junctions/${id}`, payload),
  remove: (id) => api.delete(`/v1/junctions/${id}`)
};

export const controlApi = {
  switchMode: ({ mode }) => api.post("/v1/control/switch_mode", { mode }),
  setManualTimes: (times) => api.post("/v1/control/manual_times", times),
  vipOverride: ({ lane }) => api.post("/v1/control/vip_override", { lane: Number(lane) })
};

export const commandsApi = {
  list: () => api.get("/v1/commands")
};

export default api;
