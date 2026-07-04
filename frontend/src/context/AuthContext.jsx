import { createContext, useContext, useState } from "react";
import apiClient from "../api/client";

const AuthContext = createContext(null);

function getStoredToken() {
  return localStorage.getItem("journie_token");
}

function getStoredUser() {
  const raw = localStorage.getItem("journie_user");
  return raw ? JSON.parse(raw) : null;
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getStoredToken());
  const [user, setUser] = useState(getStoredUser());

  function saveSession(data) {
    localStorage.setItem("journie_token", data.access_token);
    localStorage.setItem(
      "journie_user",
      JSON.stringify({ user_id: data.user_id, name: data.name })
    );
    setToken(data.access_token);
    setUser({ user_id: data.user_id, name: data.name });
  }

  async function signup(name, email, password) {
    const response = await apiClient.post("/auth/signup", { name, email, password });
    saveSession(response.data);
  }

  async function login(email, password) {
    const response = await apiClient.post("/auth/login", { email, password });
    saveSession(response.data);
  }

  function logout() {
    localStorage.removeItem("journie_token");
    localStorage.removeItem("journie_user");
    setToken(null);
    setUser(null);
  }

  const value = { token, user, isAuthenticated: !!token, signup, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}