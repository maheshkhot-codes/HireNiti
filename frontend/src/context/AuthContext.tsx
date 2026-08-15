import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

export type UserRole =
  | "candidate"
  | "recruiter"
  | null;

interface AuthContextType {
  token: string | null;
  role: UserRole;
  isAuthenticated: boolean;

  login: (
    token: string,
    role: UserRole
  ) => void;

  logout: () => void;
}

const AuthContext =
  createContext<AuthContextType | null>(
    null
  );

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({
  children,
}: AuthProviderProps) {

  const [token, setToken] =
    useState<string | null>(
      localStorage.getItem(
        "access_token"
      )
    );

  const [role, setRole] =
    useState<UserRole>(
      localStorage.getItem(
        "user_role"
      ) as UserRole
    );

  function login(
    newToken: string,
    newRole: UserRole
  ) {
    localStorage.setItem(
      "access_token",
      newToken
    );

    if (newRole) {
      localStorage.setItem(
        "user_role",
        newRole
      );
    }

    setToken(newToken);
    setRole(newRole);
  }

  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_role"
    );

    setToken(null);
    setRole(null);
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        role,
        isAuthenticated:
          Boolean(token),
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {

  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}