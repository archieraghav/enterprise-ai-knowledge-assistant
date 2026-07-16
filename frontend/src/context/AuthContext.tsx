import { createContext, useContext, useState, useEffect, type ReactNode } from "react";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthContextValue {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_STORAGE_KEY = "knowledge_assistant_token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const storedToken = sessionStorage.getItem(TOKEN_STORAGE_KEY);
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    sessionStorage.setItem(TOKEN_STORAGE_KEY, newToken);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}