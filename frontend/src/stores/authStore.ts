import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "../types/auth.types";

interface AuthStoreState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (user: User, accessToken: string) => void;
  logout: () => void;
  updateAccessToken: (token: string) => void;
}

export const useAuthStore = create<AuthStoreState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      login: (user, accessToken) =>
        set({
          user,
          accessToken,
          isAuthenticated: true,
        }),
      logout: () =>
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
        }),
      updateAccessToken: (token) =>
        set({
          accessToken: token,
        }),
    }),
    {
      name: "covid19-auth-storage",
    }
  )
);

