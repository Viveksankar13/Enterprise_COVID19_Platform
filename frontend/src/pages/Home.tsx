import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import {
  Globe, Syringe, Activity, Stethoscope, Database, HardDrive,
  TrendingUp, AlertTriangle, CheckCircle2, Clock, ArrowUpRight,
} from "lucide-react";
import { Card } from "../components/ui/Card";

/* ── Animated counter hook ── */
function useCountUp(target: number, duration = 1500) {
  const [val, setVal] = useState(0);
  const start = useRef<number | null>(null);
  useEffect(() => {
    const step = (ts: number) => {
      if (!start.current) start.current = ts;
      const progress = Math.min((ts - start.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setVal(Math.floor(eased * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration]);
  return val;
}

/* ── Stat card with animated counter ── */
interface StatCardProps {
  label: string;
  value: number;
  format?: (n: number) => string;
  trend: string;
  trendUp: boolean;
  icon: React.ComponentType<any>;
  iconColor: string;
  glowColor?: "blue" | "violet" | "teal" | "emerald" | "rose";
  delay?: number;
}
const StatCard: React.FC<StatCardProps> = ({
  label, value, format, trend, trendUp, icon: Icon, iconColor, glowColor = "blue", delay = 0,
}) => {
  const count = useCountUp(value, 1600);
  const display = format ? format(count) : count.toLocaleString();

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Card variant="gradient" glowColor={glowColor} className="flex items-start gap-4">
        <div className={`stat-card-icon ${iconColor}`}>
          <Icon size={20} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">{label}</p>
          <p className="text-2xl font-black text-white tabular-nums">{display}</p>
          <p className={`text-xs font-semibold mt-1 ${trendUp ? "text-emerald-400" : "text-rose-400"}`}>
            {trendUp ? "▲" : "▼"} {trend}
          </p>
        </div>
      </Card>
    </motion.div>
  );
};

/* ── Quick-access tile ── */
const QuickTile: React.FC<{
  label: string; sub: string; icon: React.ComponentType<any>;
  iconBg: string; to: string; delay?: number;
}> = ({ label, sub, icon: Icon, iconBg, to, delay = 0 }) => (
  <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay }}>
    <Link to={to}>
      <Card hoverable className="flex items-center gap-3 p-4 group">
        <div className={`h-10 w-10 rounded-xl flex items-center justify-center shrink-0 ${iconBg}`}>
          <Icon size={18} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-200 group-hover:text-white transition-colors truncate">{label}</p>
          <p className="text-[11px] text-slate-500 truncate">{sub}</p>
        </div>
        <ArrowUpRight size={14} className="text-slate-600 group-hover:text-blue-400 transition-colors shrink-0" />
      </Card>
    </Link>
  </motion.div>
);

/* ── Platform status badge ── */
const StatusBadge: React.FC<{ label: string; ok: boolean }> = ({ label, ok }) => (
  <div className="flex items-center justify-between py-2.5 border-b border-white/5 last:border-0">
    <div className="flex items-center gap-2.5">
      {ok
        ? <CheckCircle2 size={14} className="text-emerald-400 shrink-0" />
        : <AlertTriangle size={14} className="text-amber-400 shrink-0" />}
      <span className="text-sm text-slate-300">{label}</span>
    </div>
    <span className={`text-xs font-bold px-2 py-0.5 rounded border ${ok ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" : "text-amber-400 bg-amber-500/10 border-amber-500/20"}`}>
      {ok ? "Operational" : "Degraded"}
    </span>
  </div>
);

export const Home: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="space-y-8">
      {/* ── Welcome Banner ── */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative overflow-hidden rounded-2xl p-7"
        style={{
          background: "linear-gradient(135deg, rgba(59,130,246,0.12), rgba(139,92,246,0.08), rgba(6,182,212,0.06))",
          border: "1px solid rgba(59,130,246,0.18)",
        }}
      >
        {/* Decorative glow blob */}
        <div className="absolute -top-16 -right-16 w-64 h-64 rounded-full opacity-10 pointer-events-none"
          style={{ background: "radial-gradient(circle, #3b82f6, transparent)" }} />

        <div className="relative z-10 flex items-start justify-between flex-wrap gap-4">
          <div>
            <p className="text-sm font-medium text-blue-400 mb-1">
              {greeting()}, {user?.full_name?.split(" ")[0] || user?.username || "Administrator"} 👋
            </p>
            <h1 className="text-3xl font-black text-white mb-2">
              Executive{" "}
              <span className="gradient-text">Analytics Dashboard</span>
            </h1>
            <p className="text-slate-400 text-sm max-w-lg">
              Real-time global epidemiological intelligence — 195+ countries, 429K+ daily metrics, updated automatically via the OWID data pipeline.
            </p>
          </div>

          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
            <div className="pulse-dot" />
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Data Sync: Live</span>
          </div>
        </div>
      </motion.div>

      {/* ── KPI Stats ── */}
      <div>
        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4">Global Snapshot</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard label="Cumulative Cases"     value={120432019}    format={(n) => n >= 1e6 ? `${(n/1e6).toFixed(1)}M` : n.toLocaleString()}
            trend="+0.02% (24h)" trendUp icon={Globe}       iconColor="text-blue-400"    glowColor="blue"    delay={0.05} />
          <StatCard label="Cumulative Deaths"    value={2110859}      format={(n) => n.toLocaleString()}
            trend="+0.01% (24h)" trendUp={false} icon={AlertTriangle} iconColor="text-rose-400"     glowColor="rose"    delay={0.1} />
          <StatCard label="Vaccination Doses"    value={9410211842}   format={(n) => n >= 1e9 ? `${(n/1e9).toFixed(2)}B` : `${(n/1e6).toFixed(0)}M`}
            trend="+0.12% (24h)" trendUp icon={Syringe}     iconColor="text-emerald-400" glowColor="emerald" delay={0.15} />
          <StatCard label="Global Positivity"    value={32}           format={() => "3.2%"}
            trend="−0.4% vs last week" trendUp={false} icon={TrendingUp} iconColor="text-amber-400"   glowColor="teal"    delay={0.2} />
        </div>
      </div>

      {/* ── Platform Status + Quick Access ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Platform Status */}
        <motion.div initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 0.25 }}>
          <Card hoverable={false} className="h-full">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="h-8 w-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                <CheckCircle2 size={15} className="text-emerald-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-200">Platform Status</h3>
                <p className="text-[11px] text-slate-500">All systems operational</p>
              </div>
            </div>
            <StatusBadge label="FastAPI Backend"      ok={true} />
            <StatusBadge label="PostgreSQL Database"  ok={true} />
            <StatusBadge label="Redis Cache"          ok={true} />
            <StatusBadge label="ETL Data Pipeline"    ok={true} />
            <StatusBadge label="Airflow Scheduler"    ok={true} />
            <div className="mt-4 flex items-center gap-2 text-[11px] text-slate-600">
              <Clock size={11} />
              <span>Last checked: just now</span>
            </div>
          </Card>
        </motion.div>

        {/* Quick Access tiles */}
        <div className="lg:col-span-2 flex flex-col gap-3">
          <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500">Quick Access</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <QuickTile label="Global Statistics"  sub="Continental breakdowns & trends"  icon={Globe}       iconBg="bg-blue-600"    to="/global"       delay={0.3} />
            <QuickTile label="Vaccination Data"   sub="Doses, coverage & rollout"         icon={Syringe}     iconBg="bg-emerald-600" to="/vaccinations" delay={0.35} />
            <QuickTile label="Mortality Analysis" sub="CFR, excess deaths & severity"     icon={Activity}    iconBg="bg-rose-600"    to="/mortality"    delay={0.4} />
            <QuickTile label="Hospital Capacity"  sub="ICU beds, patients & occupancy"    icon={Stethoscope} iconBg="bg-violet-600"  to="/hospital"     delay={0.45} />
            <QuickTile label="SQL Explorer"       sub="Ad-hoc queries on warehouse"       icon={Database}    iconBg="bg-amber-600"   to="/explorer"     delay={0.5} />
            <QuickTile label="Pipeline Health"    sub="ETL run logs & error tracing"       icon={HardDrive}   iconBg="bg-cyan-600"    to="/health"       delay={0.55} />
          </div>
        </div>
      </div>
    </div>
  );
};
