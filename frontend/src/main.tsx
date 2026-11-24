import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { useThemeStore } from "./stores/themeStore";

// Initialize application theme state at boot
const theme = useThemeStore.getState().theme;
const root = window.document.documentElement;
root.classList.remove("light", "dark");
root.classList.add(theme);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
