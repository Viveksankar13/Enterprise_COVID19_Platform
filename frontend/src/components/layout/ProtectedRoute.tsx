import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";

interface ProtectedRouteProps {
  children: React.ReactElement;
  allowedRoles?: ("admin" | "analyst" | "viewer" | "api_user")[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
}) => {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated || !user) {
    // Redirect to login page, preserving path history
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  const roleName = user.role?.name;
  
  if (allowedRoles && !allowedRoles.includes(roleName)) {
    // Redirect unauthorized roles
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};
