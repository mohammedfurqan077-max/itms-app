import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/router";
import { authApi } from "@/services/api";
import { disconnectSocket } from "@/services/socket";
import { getRoleHome, normalizeRole } from "@/utils/roles";

const AuthContext = createContext(null);

function readStoredUser() {
  try {
    const storedUser = localStorage.getItem("itms_user");
    return storedUser ? JSON.parse(storedUser) : null;
  } catch {
    localStorage.removeItem("itms_user");
    return null;
  }
}

export function AuthProvider({ children }) {
  const router = useRouter();
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);
  const [role, setRole] = useState(null);

  useEffect(() => {
    async function hydrateAuth() {
      const storedToken = localStorage.getItem("itms_token");
      const parsedUser = readStoredUser();

      setToken(storedToken);
      setUser(parsedUser);
      setRole(normalizeRole(parsedUser?.role));

      if (storedToken) {
        try {
          const response = await authApi.me();
          const nextUser = response.data?.user || response.data;
          localStorage.setItem("itms_user", JSON.stringify(nextUser));
          setUser(nextUser);
          setRole(normalizeRole(nextUser?.role));
        } catch {
          setRole(normalizeRole(parsedUser?.role));
        }
      }

      setReady(true);
    }

    hydrateAuth();
  }, []);

  const login = useCallback(
    async (email, password) => {
      const response = await authApi.login(email, password);
      const payload = response.data;
      const jwt = payload.token || payload.access_token || payload.jwt || payload.tokens?.access_token;

      if (!jwt) {
        throw new Error("Login succeeded but no JWT was returned.");
      }

      const nextUser = payload.user || { email };
      localStorage.setItem("itms_token", jwt);
      localStorage.setItem("itms_user", JSON.stringify(nextUser));
      setToken(jwt);
      setUser(nextUser);
      const nextRole = normalizeRole(nextUser?.role);
      setRole(nextRole);
      router.replace(getRoleHome(nextRole));
    },
    [router]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("itms_token");
    localStorage.removeItem("itms_user");
    setToken(null);
    setUser(null);
    setRole(null);
    disconnectSocket();
    router.replace("/login");
  }, [router]);

  const value = useMemo(
    () => ({
      token,
      user,
      role,
      ready,
      isAuthenticated: Boolean(token),
      login,
      logout
    }),
    [login, logout, ready, role, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
