import React, { useState, useRef, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { useThemeStore } from "../../stores/themeStore";
import { Sun, Moon, LogOut, Bell, Search, ChevronDown, User, Settings, X } from "lucide-react";

/* Map path to readable page name */
const PAGE_NAMES: Record<string, string> = {
  "/":            "Home Dashboard",
  "/global":      "Global Statistics",
  "/comparison":  "Country Comparison",
  "/vaccinations":"Vaccination Analytics",
  "/mortality":   "Mortality Burden",
  "/hospital":    "Hospital Capacity",
  "/powerbi":     "Power BI Analytics",
  "/explorer":    "SQL Explorer",
  "/docs":        "API Documentation",
  "/etl-status":  "ETL Pipeline Status",
  "/health":      "Pipeline Health",
  "/users":       "User Management",
};

export const TopBar: React.FC = () => {
  const { theme, toggleTheme } = useThemeStore();
  const { user, logout } = useAuthStore();
  const location = useLocation();

  const [searchOpen, setSearchOpen] = useState(false);
  const [searchVal, setSearchVal] = useState("");
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [time, setTime] = useState(new Date());

  const searchRef = useRef<HTMLInputElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);

  const pageName = PAGE_NAMES[location.pathname] ?? "Dashboard";

  /* Clock */
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  /* Focus search on open */
  useEffect(() => {
    if (searchOpen) searchRef.current?.focus();
  }, [searchOpen]);

  /* Close user menu on outside click */
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const roleColor: Record<string, string> = {
    admin:    "text-blue-400 bg-blue-500/15 border-blue-500/25",
    analyst:  "text-violet-400 bg-violet-500/15 border-violet-500/25",
    viewer:   "text-emerald-400 bg-emerald-500/15 border-emerald-500/25",
    api_user: "text-amber-400 bg-amber-500/15 border-amber-500/25",
  };
  const role = user?.role?.name || "viewer";

  return (
    <header className="glass-panel border-b border-white/5 h-16 sticky top-0 z-20 flex items-center justify-between px-5 gap-4">
      {/* ── Breadcrumb ── */}
      <div className="flex items-center gap-2 min-w-0">
        <span className="text-slate-500 text-xs hidden sm:block">Portal</span>
        <span className="text-slate-600 text-xs hidden sm:block">/</span>
        <span className="text-sm font-semibold text-slate-200 truncate">{pageName}</span>
      </div>

      {/* ── Right controls ── */}
      <div className="flex items-center gap-2 ml-auto shrink-0">

        {/* Search */}
        <div className="relative flex items-center">
          {searchOpen ? (
            <div className="flex items-center gap-2 bg-white/5 border border-white/15 rounded-xl px-3 py-1.5 w-64 transition-all">
              <Search size={14} className="text-slate-400 shrink-0" />
              <input
                ref={searchRef}
                value={searchVal}
                onChange={(e) => setSearchVal(e.target.value)}
                placeholder="Search countries, metrics..."
                className="bg-transparent text-sm text-slate-200 placeholder-slate-500 outline-none flex-1 min-w-0"
              />
              <button onClick={() => { setSearchOpen(false); setSearchVal(""); }}
                className="text-slate-500 hover:text-slate-300 transition-colors">
                <X size={14} />
              </button>
            </div>
          ) : (
            <button
              id="topbar-search"
              onClick={() => setSearchOpen(true)}
              className="p-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
            >
              <Search size={18} />
            </button>
          )}
        </div>

        {/* Live clock */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/5 border border-white/10">
          <div className="pulse-dot scale-75" />
          <span className="text-[11px] font-mono text-slate-400 tabular-nums">
            {time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
          </span>
        </div>

        {/* Notifications */}
        <button id="topbar-notifications" className="p-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors relative">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-blue-500" />
        </button>

        {/* Theme toggle */}
        <button
          id="topbar-theme"
          onClick={toggleTheme}
          className="p-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <div className="h-5 w-px bg-white/10" />

        {/* User avatar dropdown */}
        {user ? (
          <div className="relative" ref={userMenuRef}>
            <button
              id="topbar-user-menu"
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 pl-1 pr-2 py-1 rounded-xl hover:bg-white/5 transition-colors"
            >
              <div
                className="h-8 w-8 rounded-full flex items-center justify-center text-xs font-black text-white"
                style={{ background: "linear-gradient(135deg,#3b82f6,#8b5cf6)", boxShadow: "0 0 10px rgba(59,130,246,0.3)" }}
              >
                {user.username?.charAt(0).toUpperCase()}
              </div>
              <div className="hidden md:flex flex-col items-start">
                <span className="text-xs font-semibold text-slate-200 leading-none">{user.username}</span>
                <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase tracking-wider mt-0.5 ${roleColor[role]}`}>
                  {role}
                </span>
              </div>
              <ChevronDown size={13} className="text-slate-500 hidden md:block" />
            </button>

            {/* Dropdown */}
            {userMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-52 glass-panel rounded-xl border border-white/10 shadow-2xl py-1 z-50">
                <div className="px-4 py-3 border-b border-white/5">
                  <p className="text-sm font-semibold text-slate-200">{user.full_name || user.username}</p>
                  <p className="text-xs text-slate-500 truncate">{user.email}</p>
                </div>
                <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors">
                  <User size={15} />
                  <span>Profile</span>
                </button>
                <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors">
                  <Settings size={15} />
                  <span>Settings</span>
                </button>
                <div className="border-t border-white/5 mt-1" />
                <button
                  id="topbar-logout"
                  onClick={() => { setUserMenuOpen(false); logout(); }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <LogOut size={15} />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <span className="text-sm font-semibold text-slate-500">Guest Mode</span>
        )}
      </div>
    </header>
  );
};
