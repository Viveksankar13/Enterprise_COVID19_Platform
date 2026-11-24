import { create } from "zustand";

interface ThemeStoreState {
  theme: "light" | "dark";
  toggleTheme: () => void;
  setTheme: (theme: "light" | "dark") => void;
}

export const useThemeStore = create<ThemeStoreState>((set) => ({
  theme: (localStorage.getItem("theme") as "light" | "dark") || "dark",
  toggleTheme: () =>
    set((state) => {
      const nextTheme = state.theme === "dark" ? "light" : "dark";
      localStorage.setItem("theme", nextTheme);
      
      const root = window.document.documentElement;
      root.classList.remove("light", "dark");
      root.classList.add(nextTheme);
      
      return { theme: nextTheme };
    }),
  setTheme: (theme) =>
    set(() => {
      localStorage.setItem("theme", theme);
      const root = window.document.documentElement;
      root.classList.remove("light", "dark");
      root.classList.add(theme);
      return { theme };
    }),
}));
