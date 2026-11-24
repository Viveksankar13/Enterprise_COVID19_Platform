import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { Shield, Activity, Globe, Eye, EyeOff, ArrowRight } from "lucide-react";

/* Floating virus particle */
const Particle: React.FC<{ style: React.CSSProperties }> = ({ style }) => (
  <div
    className="absolute rounded-full opacity-10 pointer-events-none"
    style={{
      background: "radial-gradient(circle, #3b82f6, transparent)",
      ...style,
    }}
  />
);

const PARTICLES = [
  { width: 120, height: 120, top: "8%",  left: "6%",  animDuration: "8s"  },
  { width: 80,  height: 80,  top: "70%", left: "12%", animDuration: "11s" },
  { width: 60,  height: 60,  top: "40%", left: "2%",  animDuration: "9s"  },
  { width: 100, height: 100, top: "15%", left: "80%", animDuration: "13s" },
  { width: 55,  height: 55,  top: "75%", left: "88%", animDuration: "7s"  },
  { width: 90,  height: 90,  top: "55%", left: "70%", animDuration: "10s" },
];

const LIVE_STATS = [
  { label: "Countries Tracked", value: "195+" },
  { label: "Daily Metrics Loaded", value: "429K" },
  { label: "Vaccination Records", value: "195K" },
  { label: "Data Pipeline Health", value: "100%" },
];

import api from "../../services/api";

export const Login: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const res = await api.post("/auth/login", {
        username,
        password,
      });
      
      // Store user and real access token in Zustand auth store
      login(res.data.user, res.data.access_token);
      navigate("/");
    } catch (err: any) {
      console.error("Login failed:", err);
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string" 
          ? detail 
          : "Invalid credentials. Hint: use admin / admin"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex login-bg overflow-hidden">
      {/* ── Left brand panel ── */}
      <motion.div
        className="hidden lg:flex w-[55%] flex-col justify-between p-12 relative overflow-hidden"
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
      >
        {/* Floating particles */}
        {PARTICLES.map((p, i) => (
          <Particle
            key={i}
            style={{
              width: p.width,
              height: p.height,
              top: p.top,
              left: p.left,
              animation: `aurora-drift ${p.animDuration} ease-in-out infinite alternate`,
            }}
          />
        ))}

        {/* Brand mark */}
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="h-10 w-10 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
              <Activity size={22} className="text-blue-400" />
            </div>
            <span className="text-sm font-bold tracking-[0.12em] uppercase text-blue-300 opacity-80">
              COVID-19 Enterprise
            </span>
          </div>

          <h1 className="text-5xl font-black leading-tight mt-8 mb-4">
            <span className="gradient-text">Global Pandemic</span>
            <br />
            <span className="text-white">Analytics Portal</span>
          </h1>

          <p className="text-slate-400 text-base leading-relaxed max-w-md">
            A unified intelligence platform for epidemiological surveillance, vaccination tracking, and real-time 
            mortality analysis — powered by enterprise-grade data pipelines.
          </p>
        </div>

        {/* Live stats grid */}
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4">
            <div className="pulse-dot" />
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Live Platform Statistics
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {LIVE_STATS.map((s) => (
              <div
                key={s.label}
                className="glass-panel rounded-xl p-4 border border-white/5"
              >
                <p className="text-2xl font-black text-white mb-0.5">{s.value}</p>
                <p className="text-xs text-slate-400">{s.label}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 flex items-center gap-4">
            <Globe size={14} className="text-slate-500" />
            <span className="text-xs text-slate-500">
              Data sourced from Our World In Data • Updated daily via automated ETL
            </span>
          </div>
        </div>
      </motion.div>

      {/* ── Right login panel ── */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          className="w-full max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {/* Mobile brand */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="h-8 w-8 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
              <Activity size={16} className="text-blue-400" />
            </div>
            <span className="text-sm font-bold tracking-wider text-blue-300">COVID-19 Enterprise</span>
          </div>

          {/* Form card */}
          <div className="glass-panel rounded-2xl gradient-border p-8 shadow-2xl">
            {/* Header */}
            <div className="flex flex-col items-start mb-8">
              <div className="h-12 w-12 rounded-xl mb-4 flex items-center justify-center"
                style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)", boxShadow: "0 0 24px rgba(59,130,246,0.35)" }}>
                <Shield size={24} className="text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white">Welcome back</h2>
              <p className="text-sm text-slate-400 mt-1">
                Sign in to access your analytics dashboard
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Username field */}
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
                  Username
                </label>
                <input
                  id="login-username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. admin"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500
                    focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50
                    transition-all duration-200 hover:border-white/20"
                />
              </div>

              {/* Password field */}
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="login-password"
                    type={showPassword ? "text" : "password"}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pr-12 text-sm text-white placeholder-slate-500
                      focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50
                      transition-all duration-200 hover:border-white/20"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* Error message */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -8, height: 0 }}
                    animate={{ opacity: 1, y: 0, height: "auto" }}
                    exit={{ opacity: 0, y: -8, height: 0 }}
                    className="px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-400 text-xs font-medium"
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Submit */}
              <button
                id="login-submit"
                type="submit"
                disabled={isLoading}
                className="w-full py-3 rounded-xl font-bold text-sm text-white flex items-center justify-center gap-2
                  transition-all duration-200 hover:opacity-90 hover:shadow-lg hover:shadow-blue-500/25
                  disabled:opacity-60 disabled:cursor-not-allowed"
                style={{ background: "linear-gradient(135deg, #3b82f6, #6366f1)" }}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Authenticating...
                  </span>
                ) : (
                  <>
                    Sign In to Dashboard
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            {/* Demo hint */}
            <div className="mt-5 p-3 rounded-xl bg-blue-500/8 border border-blue-500/15">
              <p className="text-center text-xs text-slate-500">
                <span className="text-slate-400 font-medium">Demo credentials:</span>{" "}
                <code className="font-mono text-blue-400">admin</code> /{" "}
                <code className="font-mono text-blue-400">admin</code>
              </p>
            </div>
          </div>

          {/* Footer note */}
          <p className="text-center text-xs text-slate-600 mt-6">
            Enterprise COVID-19 Analytics Platform &copy; 2024
          </p>
        </motion.div>
      </div>
    </div>
  );
};
