import {
  Navigate,
  Outlet,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

interface ProtectedRouteProps {
  allowedRole?:
    | "candidate"
    | "recruiter";
}

export default function ProtectedRoute({
  allowedRole,
}: ProtectedRouteProps) {

  const {
    isAuthenticated,
    role,
  } = useAuth();

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  if (
    allowedRole &&
    role !== allowedRole
  ) {
    return (
      <Navigate
        to="/"
        replace
      />
    );
  }

  return <Outlet />;
}