export interface Role {
  role_id: number;
  name: "admin" | "analyst" | "viewer" | "api_user";
  description?: string;
  is_active: boolean;
}

export interface Permission {
  permission_id: number;
  role_id: number;
  resource: string;
  action: string;
}

export interface User {
  user_id: string;
  email: string;
  username: string;
  full_name?: string;
  role: Role;
  is_active: boolean;
  is_verified: boolean;
  last_login_at?: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
}
